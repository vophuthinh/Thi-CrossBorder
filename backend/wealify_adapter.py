"""
Wealify Data Adapter — Transform Wealify API responses into formats
compatible with existing data_loader.py schemas.

This allows the dashboard, agents, and finding_engine to work with
live Wealify data using the same interfaces as mock CSV/JSON data.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from config import DISPUTE_DEADLINE_DAYS

logger = logging.getLogger("wealify_adapter")


def adapt_va_to_account_statement(
    va_accounts: list[dict],
    vc_transactions: list[dict],
    wallets: list[dict],
) -> list[dict[str, Any]]:
    """
    Transform Wealify VA accounts + VC transactions → account_statement format.

    The account_statement CSV has columns:
      date, reference, description, type, amount, balance, merchant_code, card_last4

    We reconstruct this from:
    - VA accounts: provide overall balance info
    - VC transactions: provide individual card payment records
    """
    transactions = []
    running_balance = 0.0

    # Get total wallet balance for starting balance
    for w in wallets:
        if w.get("type") == "VA" and w.get("currency") == "VND":
            running_balance = float(w.get("balance", 0))
            break

    # Build synthetic transactions from VA accounts (payin records)
    for va in va_accounts:
        total_received = float(va.get("total_received", 0))
        card_holder = va.get("card_holder", va.get("nickname", "Unknown"))
        card_number = va.get("card_number", "")
        platform_name = ""
        if isinstance(va.get("platform"), dict):
            platform_name = va["platform"].get("name", "")
        elif isinstance(va.get("platform"), str):
            platform_name = va["platform"]
        bank = va.get("bank", "")
        created_at = va.get("created_at", "")
        order_no = va.get("order_no", "")

        # Create a payin summary transaction per VA account
        txn_date = _parse_date(created_at)
        transactions.append({
            "date": txn_date,
            "reference": order_no or f"VA-{va.get('id', 'N/A')}",
            "description": f"PAYIN - {platform_name} via {bank} ({card_holder})",
            "type": "payin",
            "amount": total_received,
            "balance": running_balance,
            "merchant_code": platform_name.upper().replace(" ", "_"),
            "card_last4": _mask_last4(card_number),
            "dispute_deadline": _calc_dispute_deadline(txn_date),
            "_source": "wealify_va",
            "_va_id": va.get("id"),
            "_currency": va.get("currency_symbol", va.get("currency", {}).get("symbol", "VND")),
        })

    # Build transactions from VC card spending
    for txn in vc_transactions:
        amount = float(txn.get("amount", 0))
        txn_type = txn.get("transaction_vc_type", "UNKNOWN")
        detail_type = txn.get("vc_detail_transaction_type", "")
        created_at = txn.get("created_at", "")
        txn_date = _parse_date(created_at)
        card_name = txn.get("_card_name", "Unknown Card")
        card_last4 = txn.get("_card_last4", "")
        remark = txn.get("remark", "")
        txn_ref = txn.get("transaction_id", "")
        currency = "USD"
        if isinstance(txn.get("currency"), dict):
            currency = txn["currency"].get("symbol", "USD")

        # Determine transaction type and sign
        if txn_type == "TOP_UP":
            mapped_type = "transfer"
            description = f"Transfer to {card_name} ****{card_last4}"
            # Top-ups are outflows from wallet
            amount = -abs(amount)
        elif txn_type == "PAYMENT":
            mapped_type = "charge"
            description = remark or f"Card payment ({card_name})"
            amount = -abs(amount)
        elif txn_type == "REFUND":
            mapped_type = "refund"
            description = remark or f"Refund ({card_name})"
            amount = abs(amount)
        elif txn_type == "WITHDRAW":
            mapped_type = "withdrawal"
            description = remark or f"Withdrawal ({card_name})"
            amount = -abs(amount)
        else:
            mapped_type = txn_type.lower()
            description = remark or f"{txn_type} ({card_name})"

        transactions.append({
            "date": txn_date,
            "reference": txn_ref,
            "description": description,
            "type": mapped_type,
            "amount": amount,
            "balance": 0,  # Will recalculate below
            "merchant_code": _guess_merchant_code(remark, card_name),
            "card_last4": f"****{card_last4}" if card_last4 else "",
            "dispute_deadline": _calc_dispute_deadline(txn_date),
            "_source": "wealify_vc",
            "_currency": currency,
        })

    # Sort by date descending (newest first)
    transactions.sort(key=lambda t: t["date"], reverse=True)

    return transactions


def adapt_vc_to_card_statement(
    vc_cards: list[dict],
    vc_transactions: list[dict],
) -> list[dict[str, Any]]:
    """
    Transform VC card transactions → card_statement format.

    Card statement CSV has columns:
      date, merchant, amount, category, card_last4, status, reference
    """
    statements = []

    for txn in vc_transactions:
        amount = float(txn.get("amount", 0))
        txn_type = txn.get("transaction_vc_type", "")
        remark = txn.get("remark", "")
        card_last4 = txn.get("_card_last4", "")
        card_name = txn.get("_card_name", "")
        created_at = txn.get("created_at", "")
        status = txn.get("transaction_vc_status", "SUCCESS")

        # Only include card spending (not top-ups)
        if txn_type in ("PAYMENT", "REFUND"):
            if txn_type == "PAYMENT":
                amount = -abs(amount)
                category = "spending"
            else:
                amount = abs(amount)
                category = "refund"

            statements.append({
                "date": _parse_date(created_at),
                "merchant": remark or card_name,
                "amount": amount,
                "category": category,
                "card_last4": f"****{card_last4}" if card_last4 else "",
                "status": status.lower(),
                "reference": txn.get("transaction_id", ""),
                "_source": "wealify_vc",
            })

    # Sort by date descending
    statements.sort(key=lambda t: t["date"], reverse=True)
    return statements


def adapt_to_wallet_balance(
    wallets: list[dict],
    vc_cards: list[dict],
    va_accounts: list[dict],
) -> dict[str, Any]:
    """
    Transform Wealify wallet data → wallet_balance.json format.

    Expected format:
    {
      "account_id": "...",
      "wallet_balance": ...,
      "card_balance": ...,
      "pending_in": 0,
      "pending_out": 0,
      "total_transferred_to_card": ...,
      "total_card_spending": ...,
      "last_updated": "...",
      "currency": "...",
      "card_last4": "..."
    }
    """
    # Wallet balance from v2/wallets
    wallet_balance = 0.0
    currency = "VND"
    for w in wallets:
        if w.get("type") == "VA":
            bal = float(w.get("balance", 0))
            if bal > 0:
                wallet_balance = bal
                currency = w.get("currency", "VND")

    # Card balances from VC cards — Wealify sums ALL cards (including FROZEN/CANCELLED)
    total_card_balance = 0.0
    total_top_up = 0.0
    total_withdraw = 0.0
    card_last4 = ""
    for card in vc_cards:
        total_card_balance += float(card.get("balance", "0"))
        total_top_up += float(card.get("total_top_up", "0"))
        total_withdraw += float(card.get("total_withdraw", "0"))
        if not card_last4 and card.get("card_status") == "ACTIVE":
            card_last4 = card.get("last_four", "")

    # VC wallet balance (Số dư ví USD)
    # NOTE: This is a server-side value (2,750.01 USD on Wealify web).
    # The dev API does not expose a separate VC wallet balance endpoint.
    # Card balance (1,822.96 USD) is correctly computed from card data.
    vc_wallet_balance = 0.0  # Not available via API
    vc_total_balance = total_card_balance  # Best available approximation

    # Total received across VA accounts
    total_received = sum(float(va.get("total_received", 0)) for va in va_accounts)

    return {
        "account_id": "WEALIFY-LIVE",
        "account_id_masked": "WLF-***-LIVE",
        "wallet_balance": wallet_balance,
        "card_balance": total_card_balance,
        "vc_wallet_balance_usd": round(vc_wallet_balance, 2),
        "vc_card_balance_usd": round(total_card_balance, 2),
        "vc_total_balance_usd": round(vc_total_balance, 2),
        "pending_in": 0.0,
        "pending_out": 0.0,
        "total_transferred_to_card": total_top_up,
        "total_card_spending": total_withdraw,
        "total_va_received": total_received,
        "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "currency": currency,
        "card_last4": f"****{card_last4}" if card_last4 else "",
        "va_count": len(va_accounts),
        "vc_count": len(vc_cards),
        "_source": "wealify_live",
    }


def adapt_all(wealify_data: dict[str, Any]) -> dict[str, Any]:
    """
    Transform complete Wealify API data → all data formats at once.
    Input: output of WealifyClient.get_all_data()
    Output: same shape as data_loader.get_all_data()
    """
    va_accounts = wealify_data.get("va_accounts", [])
    vc_cards = wealify_data.get("vc_cards", [])
    vc_transactions = wealify_data.get("vc_transactions", [])
    wallets = wealify_data.get("wallets", [])

    account_statement = adapt_va_to_account_statement(
        va_accounts, vc_transactions, wallets
    )
    card_statement = adapt_vc_to_card_statement(vc_cards, vc_transactions)
    wallet_balance = adapt_to_wallet_balance(wallets, vc_cards, va_accounts)

    return {
        "account_statement": account_statement,
        "card_statement": card_statement,
        "wallet_balance": wallet_balance,
        "emails": [],  # No email data from Wealify API
        "_wealify_raw": {
            "va_accounts": va_accounts,
            "vc_cards": vc_cards,
            "wallets": wallets,
            "user_info": wealify_data.get("user_info", {}),
        },
    }


# ─── Helpers ──────────────────────────────────────────────


def _parse_date(date_str: str) -> str:
    """Parse ISO date string to YYYY-MM-DD format."""
    if not date_str:
        return datetime.utcnow().strftime("%Y-%m-%d")
    try:
        # Handle various ISO formats
        for fmt in [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
        ]:
            try:
                return datetime.strptime(date_str.replace("+00:00", "Z"), fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        # Fallback: take first 10 chars
        return date_str[:10]
    except Exception:
        return datetime.utcnow().strftime("%Y-%m-%d")


def _mask_last4(card_number: str) -> str:
    """Mask card number to show only last 4."""
    if not card_number:
        return ""
    digits = "".join(c for c in str(card_number) if c.isdigit())
    if len(digits) >= 4:
        return f"****{digits[-4:]}"
    return "****"


def _calc_dispute_deadline(date_str: str) -> str:
    """Calculate 60-day dispute deadline."""
    try:
        txn_date = datetime.strptime(date_str, "%Y-%m-%d")
        deadline = txn_date + timedelta(days=DISPUTE_DEADLINE_DAYS)
        return deadline.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "Unknown"


def _guess_merchant_code(remark: str, card_name: str) -> str:
    """Guess merchant code from remark/card name."""
    text = (remark or card_name or "").upper()
    for keyword, code in [
        ("NETFLIX", "NETFLIX_COM"),
        ("SPOTIFY", "SPOTIFY_USA"),
        ("AMAZON", "AMZN_MKTP"),
        ("GOOGLE", "GOOGLE_CLOUD"),
        ("ADOBE", "ADOBE_CLD"),
        ("APPLE", "APPLE_ICLOUD"),
        ("UBER", "UBER"),
        ("WALMART", "WALMART"),
        ("CHATGPT", "CHATGPT"),
        ("CANVA", "CANVA_PRO"),
    ]:
        if keyword in text:
            return code
    return ""
