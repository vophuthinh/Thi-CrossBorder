"""
Data Loader — Parse CSV statements, emails, wallet balance.
Masks sensitive data (card numbers, account numbers).
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from config import (
    ACCOUNT_STATEMENT_PATH,
    CARD_STATEMENT_PATH,
    WALLET_BALANCE_PATH,
    EMAILS_DIR,
    DISPUTE_DEADLINE_DAYS,
)


def mask_card_number(number: str) -> str:
    """Only show last 4 digits: ****8842"""
    digits = re.sub(r"\D", "", str(number))
    if len(digits) >= 4:
        return f"****{digits[-4:]}"
    return "****"


def mask_account_number(account_id: str) -> str:
    """Mask account: WLF-***-DEMO"""
    if not account_id:
        return "***"
    parts = account_id.split("-")
    if len(parts) >= 3:
        return f"{parts[0]}-***-{parts[-1]}"
    return "***"


def load_account_statement(path: Path | None = None) -> list[dict[str, Any]]:
    """Parse account statement CSV."""
    path = path or ACCOUNT_STATEMENT_PATH
    transactions = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            txn = {
                "date": row["date"],
                "reference": row["reference"],
                "description": row["description"],
                "type": row["type"],
                "amount": float(row["amount"]),
                "balance": float(row["balance"]),
                "merchant_code": row.get("merchant_code", ""),
                "card_last4": mask_card_number(row.get("card_last4", "")) if row.get("card_last4") else "",
                "dispute_deadline": _calc_dispute_deadline(row["date"]),
            }
            transactions.append(txn)
    return transactions


def load_card_statement(path: Path | None = None) -> list[dict[str, Any]]:
    """Parse card statement CSV."""
    path = path or CARD_STATEMENT_PATH
    transactions = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            txn = {
                "date": row["date"],
                "merchant": row["merchant"],
                "amount": float(row["amount"]),
                "category": row.get("category", ""),
                "card_last4": mask_card_number(row.get("card_last4", "")),
                "status": row.get("status", ""),
                "reference": row.get("reference", ""),
            }
            transactions.append(txn)
    return transactions


def load_wallet_balance(path: Path | None = None) -> dict[str, Any]:
    """Parse wallet balance JSON."""
    path = path or WALLET_BALANCE_PATH
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Mask sensitive fields
    if "account_id" in data:
        data["account_id_masked"] = mask_account_number(data["account_id"])
    if "card_last4" in data:
        data["card_last4"] = mask_card_number(data["card_last4"])
    return data


def load_emails(email_dir: Path | None = None) -> list[dict[str, str]]:
    """
    Load emails for reconciliation. If USE_GMAIL_API=true, reads the real
    demo inbox via the Gmail API (read-only). Falls back to local .txt
    mock files on any failure or when disabled.
    """
    from config import USE_GMAIL_API

    if USE_GMAIL_API:
        try:
            from gmail_client import fetch_emails

            emails = fetch_emails()
            print(f"[data_loader] ✅ Loaded {len(emails)} emails from Gmail API")
            return emails
        except Exception as e:
            print(f"[data_loader] ⚠️ Gmail API failed ({e}), falling back to local .txt files")

    email_dir = email_dir or EMAILS_DIR
    emails = []
    if not email_dir.exists():
        return emails

    for email_file in sorted(email_dir.glob("*.txt")):
        email_data = _parse_email_file(email_file)
        if email_data:
            emails.append(email_data)
    return emails


def _parse_email_file(filepath: Path) -> dict[str, str] | None:
    """Parse a single email text file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.strip().split("\n")

        email = {
            "filename": filepath.name,
            "from": "",
            "to": "",
            "subject": "",
            "date": "",
            "body": "",
        }

        body_start = 0
        for i, line in enumerate(lines):
            lower = line.lower()
            if lower.startswith("from:"):
                email["from"] = line[5:].strip()
            elif lower.startswith("to:"):
                email["to"] = line[3:].strip()
            elif lower.startswith("subject:"):
                email["subject"] = line[8:].strip()
            elif lower.startswith("date:"):
                email["date"] = line[5:].strip()
            elif line.strip() == "" and body_start == 0:
                body_start = i + 1

        if body_start > 0:
            email["body"] = "\n".join(lines[body_start:]).strip()
        else:
            email["body"] = content

        return email
    except Exception:
        return None


def _calc_dispute_deadline(date_str: str) -> str:
    """Calculate 60-day dispute deadline from transaction date."""
    try:
        txn_date = datetime.strptime(date_str, "%Y-%m-%d")
        deadline = txn_date + timedelta(days=DISPUTE_DEADLINE_DAYS)
        return deadline.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "Unknown"


def get_all_data() -> dict[str, Any]:
    """
    Load all data sources at once.
    Always uses LIVE Wealify API data. No mock/fake data fallback.
    Local CSV files are only used if USE_LIVE_WEALIFY is explicitly set to false.
    """
    from config import USE_LIVE_WEALIFY

    if USE_LIVE_WEALIFY:
        try:
            from wealify_client import get_wealify_client
            from wealify_adapter import adapt_all

            client = get_wealify_client()
            raw_data = client.get_all_data()
            adapted = adapt_all(raw_data)

            # Merge emails (from Gmail API or local files)
            adapted["emails"] = _classify_emails_safe(load_emails())

            print("[data_loader] ✅ Loaded LIVE data from Wealify API")
            return adapted
        except Exception as e:
            print(f"[data_loader] ❌ Wealify API FAILED: {e}")
            print("[data_loader] ❌ NO fallback to fake data — fix API connection!")
            raise RuntimeError(f"Wealify API unavailable: {e}") from e

    # Only reach here if USE_LIVE_WEALIFY=false (explicitly disabled)
    print("[data_loader] ⚠️ Using LOCAL mock data (USE_LIVE_WEALIFY=false)")
    return {
        "account_statement": load_account_statement(),
        "card_statement": load_card_statement(),
        "wallet_balance": load_wallet_balance(),
        "emails": _classify_emails_safe(load_emails()),
    }


def _classify_emails_safe(emails: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    LLM-classify emails as transactional vs promotional (one batched call)
    so email_matcher.py can exclude promo emails from matching — a Shopee
    ad shouldn't be picked as the receipt for a real Shopee charge just
    because it mentions "Shopee". Runs on every data load (startup, /reset,
    each periodic scheduled check), so it re-classifies unchanged emails
    repeatedly — acceptable for now, but a real cost/latency cost if
    SCHEDULED_CHECK_INTERVAL_SECONDS is set low; caching by email content
    would be the next improvement, not done here to keep this change small.
    """
    try:
        from agents.email_classifier import classify_emails

        return classify_emails(emails)
    except Exception as e:
        print(f"[data_loader] ⚠️ Email classification failed ({e}), matching will run unfiltered")
        return emails

