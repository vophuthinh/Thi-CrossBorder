"""
Agent 3: Reconciler — Đối chiếu 3 nguồn tiền.
Account ↔ Wallet ↔ Card — bắt các lệch.
"""
from __future__ import annotations

from typing import Any


def reconcile_three_sources(
    account_txns: list[dict[str, Any]],
    card_txns: list[dict[str, Any]],
    wallet: dict[str, Any],
    lang: str = "vi",
) -> dict[str, Any]:
    """
    Cross-check 3 data sources and find discrepancies.
    """
    discrepancies = []

    # 1. Check transfers: money left account but didn't appear on card
    # USD-only: wallet["card_balance"] (compared against this further down)
    # is itself a USD-only figure (adapt_to_wallet_balance) — this account
    # has both USD and EUR cards, and mixing them here compared a
    # USD-only balance against a USD+EUR flow, producing an inflated,
    # currency-confused "mismatch".
    transfer_txns = [t for t in account_txns if t.get("type") == "transfer" and (t.get("_currency") or "USD") == "USD"]
    total_transferred = sum(abs(t["amount"]) for t in transfer_txns)

    # 2. Check charges in account vs card
    # card_txns also includes "top_up" (wallet→card transfers) and "refund"
    # entries — those map to account_statement's "transfer"/"refund" types,
    # never "charge", so comparing them against account_charges here always
    # false-flagged them as "missing" regardless of whether the data was
    # actually consistent. Real bug, not a side effect of any status
    # filter: found when live pagination made vc_transactions more
    # complete (268 → 414) and the false-positive count became impossible
    # to miss (103 of 126 "missing" were legitimate top_ups).
    # Also SUCCESS-only: a card charge still PENDING/PROCESSING or that
    # FAILED/was CANCELled never became real settled money, so it not
    # being in account_statement (SUCCESS-only, see wealify_adapter.py)
    # isn't a discrepancy to reconcile — it's expected. Unsettled ones are
    # already surfaced separately by reminder_checker.py's stale-processing
    # check instead of being double-reported here as a false "lệch".
    account_charges = {t["reference"]: t for t in account_txns if t.get("type") == "charge"}
    card_refs = {
        t["reference"]: t
        for t in card_txns
        if t.get("category") == "spending" and t.get("status") == "success"
    }

    # Find charges in account but NOT on card
    missing_on_card = []
    for ref, txn in account_charges.items():
        if ref not in card_refs:
            missing_on_card.append(txn)
            discrepancies.append({
                "type": "missing_on_card",
                "reference": ref,
                "description": txn["description"],
                "amount": txn["amount"],
                "date": txn["date"],
                "detail": _msg("Khoản này rời tài khoản nhưng KHÔNG xuất hiện trên sao kê thẻ.",
                              "This charge left the account but did NOT appear on the card statement.", lang),
                "source": "account_statement vs card_statement",
            })

    # Find charges on card but NOT in account
    for ref, txn in card_refs.items():
        if ref not in account_charges:
            discrepancies.append({
                "type": "missing_in_account",
                "reference": ref,
                "description": txn["merchant"],
                "amount": txn["amount"],
                "date": txn["date"],
                "detail": _msg("Khoản này xuất hiện trên thẻ nhưng KHÔNG có trong sao kê tài khoản.",
                              "This charge appears on the card but NOT in the account statement.", lang),
                "source": "card_statement vs account_statement",
            })

    # 3. Check duplicate charges (same amount + same merchant + same day in account)
    seen = {}
    for txn in account_txns:
        if txn.get("type") != "charge":
            continue
        key = f"{txn['date']}|{txn['description']}|{txn['amount']}"
        if key in seen:
            discrepancies.append({
                "type": "duplicate_charge",
                "reference": txn["reference"],
                "description": txn["description"],
                "amount": txn["amount"],
                "date": txn["date"],
                "detail": _msg(
                    f"Khoản trùng với {seen[key]['reference']} — cùng ngày, cùng số tiền, cùng merchant.",
                    f"Duplicate of {seen[key]['reference']} — same date, amount, and merchant.", lang),
                "source": "account_statement",
                "duplicate_of": seen[key]["reference"],
            })
        else:
            seen[key] = txn

    # 4. Check duplicate fees
    fee_seen = {}
    for txn in account_txns:
        if txn.get("type") != "fee":
            continue
        key = f"{txn['date']}|{txn['description']}|{txn['amount']}"
        if key in fee_seen:
            discrepancies.append({
                "type": "duplicate_fee",
                "reference": txn["reference"],
                "description": txn["description"],
                "amount": txn["amount"],
                "date": txn["date"],
                "detail": _msg(
                    f"Phí kép — bị tính 2 lần cùng ngày (trùng với {fee_seen[key]['reference']}).",
                    f"Double fee — charged twice on same day (duplicate of {fee_seen[key]['reference']}).", lang),
                "source": "account_statement",
                "duplicate_of": fee_seen[key]["reference"],
            })
        else:
            fee_seen[key] = txn

    # 5. Wallet balance check
    # Same bug class as the ref-matching above: this summed every card_txns
    # row regardless of category, so top_up (money arriving on the card,
    # not spent) got counted as "spending" too — inflating this total by
    # roughly the entire top_up volume. Also now includes "withdrawal"
    # (cash withdrawn from the card — previously missing from
    # card_statement entirely) as an outflow, and nets out "refund"
    # (money returned) — all real ways the card balance moves besides
    # top_up, which total_transferred already accounts for separately.
    success_card_txns = [
        t for t in card_txns
        if t.get("status") == "success" and (t.get("_currency") or "USD") == "USD"
    ]
    card_spending_total = (
        sum(abs(t["amount"]) for t in success_card_txns if t.get("category") == "spending")
        + sum(abs(t["amount"]) for t in success_card_txns if t.get("category") == "withdrawal")
        - sum(abs(t["amount"]) for t in success_card_txns if t.get("category") == "refund")
    )
    expected_card_balance = total_transferred - card_spending_total
    actual_card_balance = wallet.get("card_balance", 0)

    if abs(expected_card_balance - actual_card_balance) > 0.01:
        discrepancies.append({
            "type": "wallet_card_mismatch",
            "detail": _msg(
                f"Số dư thẻ lệch: tổng chuyển sang thẻ = ${total_transferred:.2f}, "
                f"tổng chi trên thẻ = ${card_spending_total:.2f}, "
                f"số dư thẻ kỳ vọng = ${expected_card_balance:.2f}, "
                f"số dư thẻ thực tế = ${actual_card_balance:.2f}. "
                f"Lệch ${abs(expected_card_balance - actual_card_balance):.2f}, chưa xác định nguyên nhân.",
                f"Card balance mismatch: total transferred = ${total_transferred:.2f}, "
                f"total card spending = ${card_spending_total:.2f}, "
                f"expected card balance = ${expected_card_balance:.2f}, "
                f"actual card balance = ${actual_card_balance:.2f}. "
                f"Discrepancy of ${abs(expected_card_balance - actual_card_balance):.2f}, cause undetermined.", lang),
            "source": "wallet_balance vs card_statement",
            "expected": round(expected_card_balance, 2),
            "actual": actual_card_balance,
            "difference": round(abs(expected_card_balance - actual_card_balance), 2),
        })

    return {
        "total_discrepancies": len(discrepancies),
        "discrepancies": discrepancies,
        "summary": {
            "transfers_checked": len(transfer_txns),
            "total_transferred": round(total_transferred, 2),
            "charges_on_account": len(account_charges),
            "charges_on_card": len(card_refs),
            "missing_on_card": len(missing_on_card),
        },
    }


def _msg(vi: str, en: str, lang: str) -> str:
    return en if lang == "en" else vi
