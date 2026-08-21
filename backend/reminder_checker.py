"""
Reminder Checker — Nhiệm vụ 7: configurable-threshold proactive reminders
for 2 situations:
  1. An email says money was received, but Wealify's VA-transactions API
     is broken (see agents/inbound_reconciler.py) so it can never be
     positively confirmed against a Wealify transaction code. Staying
     silent forever isn't right either — past the configured wait, it's
     worth a reminder to check manually.
  2. A real Wealify transaction has been stuck in PENDING/PROCESSING
     status longer than the configured threshold.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from agents.inbound_reconciler import check_inbound_emails

CONFIG_PATH = Path(__file__).parent / "data" / "reminder_config.json"
DEFAULT_CONFIG = {"inbound_email_hours": 24.0, "processing_status_hours": 48.0}


def load_reminder_config() -> dict[str, float]:
    if CONFIG_PATH.exists():
        try:
            saved = json.loads(CONFIG_PATH.read_text())
            return {**DEFAULT_CONFIG, **saved}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_CONFIG)


def save_reminder_config(cfg: dict[str, float]) -> dict[str, float]:
    merged = {**DEFAULT_CONFIG, **cfg}
    for key in DEFAULT_CONFIG:
        value = merged[key]
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be a finite number greater than zero")
        merged[key] = float(value)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(merged, indent=2))
    return merged


def check_stale_processing_transactions(
    card_statement: list[dict[str, Any]], threshold_hours: float, lang: str = "vi"
) -> list[dict[str, Any]]:
    """Real Wealify transactions still PENDING/PROCESSING past the
    configured threshold hours."""
    now = datetime.now(timezone.utc)
    flagged = []
    for txn in card_statement:
        status = (txn.get("status") or "").lower()
        if status not in ("pending", "processing"):
            continue
        try:
            txn_date = datetime.strptime(txn["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except (KeyError, ValueError, TypeError):
            continue
        age_hours = (now - txn_date).total_seconds() / 3600
        if age_hours < threshold_hours:
            continue
        flagged.append({
            "reference": txn.get("reference", ""),
            "merchant": txn.get("merchant", ""),
            "amount": txn.get("amount", 0),
            "date": txn.get("date", ""),
            "status": status,
            "age_hours": round(age_hours, 1),
            "reason": _msg(
                f"Giao dịch đang \"{status}\" đã {round(age_hours)} giờ, vượt ngưỡng "
                f"{threshold_hours:g} giờ đã cài đặt.",
                f"Transaction has been \"{status}\" for {round(age_hours)}h, past the "
                f"configured {threshold_hours:g}h threshold.",
                lang,
            ),
        })
    return flagged


def check_stale_unverified_inbound_emails(
    emails: list[dict[str, Any]], threshold_hours: float, lang: str = "vi"
) -> list[dict[str, Any]]:
    """Emails indicating money received that still can't be matched to a
    Wealify transaction (VA-transactions API is broken), past the
    configured wait threshold."""
    inbound = check_inbound_emails(emails, lang)
    now = datetime.now(timezone.utc)
    flagged = []
    for item in inbound["items"]:
        email_date = _parse_email_date(item.get("email_date", ""))
        if email_date is None:
            continue
        age_hours = (now - email_date).total_seconds() / 3600
        if age_hours < threshold_hours:
            continue
        flagged.append({**item, "age_hours": round(age_hours, 1)})
    return flagged


def _parse_email_date(raw: str) -> datetime | None:
    try:
        dt = parsedate_to_datetime(raw)
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        return None


def _msg(vi: str, en: str, lang: str) -> str:
    return en if lang == "en" else vi
