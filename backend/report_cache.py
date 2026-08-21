"""
Report Cache — pre-generates monthly + yearly reports so the frontend reads
a fast on-disk file instead of recomputing analyze_statement/generate_report
on every request. This is a cache of that same pipeline's output, not a
second source of truth — so it can never disagree with /dashboard/report.

Only the current month is ever regenerated after the initial run (past
months are closed, future months have no data yet), and only when a
transaction newer than the cache's own generation time has appeared.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_DIR = Path(__file__).parent / "report"


def _month_key(year: int, month: int) -> str:
    return f"{year}-{month:02d}"


def _report_path(key: str) -> Path:
    return REPORT_DIR / f"{key}.json"


def _newest_transaction_date(account_statement: list[dict]) -> str:
    dates = [t.get("date", "") for t in account_statement if t.get("date")]
    return max(dates) if dates else ""


def _build_report(transactions: list[dict], anomalies: dict, lang: str) -> dict:
    from agents.statement_parser import analyze_statement
    from agents.report_generator import generate_report

    analysis = analyze_statement(transactions, lang)
    return generate_report(analysis, anomalies, lang)


def _write_report(key: str, report: dict, newest_txn_date: str) -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "newest_txn_date_at_generation": newest_txn_date,
        "report": report,
    }
    _report_path(key).write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def generate_and_cache_reports(
    account_statement: list[dict], anomalies: dict, lang: str = "vi"
) -> None:
    """Generate one file per month of the current year up to the current
    month, plus one yearly aggregate file."""
    now = datetime.now(timezone.utc)
    newest_txn_date = _newest_transaction_date(account_statement)

    for month in range(1, now.month + 1):
        month_prefix = f"{now.year}-{month:02d}"
        month_txns = [t for t in account_statement if t.get("date", "").startswith(month_prefix)]
        report = _build_report(month_txns, anomalies, lang)
        _write_report(_month_key(now.year, month), report, newest_txn_date)

    year_report = _build_report(account_statement, anomalies, lang)
    _write_report(str(now.year), year_report, newest_txn_date)


def refresh_current_month_if_stale(
    account_statement: list[dict], anomalies: dict, lang: str = "vi"
) -> bool:
    """Regenerate the current month (+ the yearly aggregate) only if a
    transaction newer than what the cached report was built from has
    appeared. Returns True if a refresh happened."""
    now = datetime.now(timezone.utc)
    month_key = _month_key(now.year, now.month)
    path = _report_path(month_key)
    newest_txn_date = _newest_transaction_date(account_statement)

    if path.exists():
        try:
            cached = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            cached = {}
        if cached.get("newest_txn_date_at_generation", "") >= newest_txn_date:
            return False  # already up to date, nothing newer has appeared

    month_prefix = f"{now.year}-{now.month:02d}"
    month_txns = [t for t in account_statement if t.get("date", "").startswith(month_prefix)]
    report = _build_report(month_txns, anomalies, lang)
    _write_report(month_key, report, newest_txn_date)

    year_report = _build_report(account_statement, anomalies, lang)
    _write_report(str(now.year), year_report, newest_txn_date)
    return True


def get_cached_report(key: str) -> dict[str, Any] | None:
    path = _report_path(key)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def list_cached_keys(year: int) -> dict[str, Any]:
    months = sorted(p.stem for p in REPORT_DIR.glob(f"{year}-*.json"))
    return {"months": months, "year": str(year) if _report_path(str(year)).exists() else None}
