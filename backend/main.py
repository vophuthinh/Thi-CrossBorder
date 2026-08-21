"""
Wealify Smart Finance — FastAPI Backend
Dashboard-first API + AI Chatbot
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import (
    DEMO_MODE,
    DISCLAIMER_VI,
    DISCLAIMER_EN,
    BYTEPLUS_API_KEY,
    SCHEDULED_CHECK_INTERVAL_SECONDS,
    CURRENCY_SYMBOLS,
    USER_EMAIL,
)
from chat import ChatOrchestrator
from audit_log import audit_log
from data_loader import get_all_data
from agents.statement_parser import analyze_statement
from agents.anomaly_detector import detect_anomalies
from agents.reconciler import reconcile_three_sources
from agents.email_matcher import match_transactions_to_emails, get_match_summary
from agents.report_generator import generate_report, income_note
from agents.risk_scorer import calculate_risk_score
from finding_engine import generate_all_findings

logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    report_task = asyncio.create_task(_pre_generate_reports())
    task = asyncio.create_task(_periodic_check_loop())
    yield
    report_task.cancel()
    task.cancel()


app = FastAPI(
    title="Wealify Smart Finance",
    description="AI-powered Dashboard for expense management & transaction safety",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from setup_api import router as setup_router
app.include_router(setup_router)

# --- Preload data (once) ---
_data = get_all_data()

import report_cache
import reminder_checker


async def _pre_generate_reports() -> None:
    """Generate the twelve monthly reports and yearly report in the background."""
    try:
        await asyncio.to_thread(
            report_cache.generate_and_cache_reports,
            _data["account_statement"],
            detect_anomalies(_data["account_statement"], "vi"),
            "vi",
        )
        logger.info("[report-cache] pre-generated monthly and yearly reports")
    except Exception as e:
        logger.warning("[report-cache] initial generation failed: %s", e)

# Global chat orchestrator (per-server session for demo)
orchestrator = ChatOrchestrator()


# ─── Models ──────────────────────────────────────────────


class ChatRequest(BaseModel):
    message: str


class InsightRequest(BaseModel):
    context: str = "general"


class ReminderConfigRequest(BaseModel):
    inbound_email_hours: float = Field(gt=0)
    processing_status_hours: float = Field(gt=0)


class ReportEmailRequest(BaseModel):
    period_type: str  # month | quarter | year
    period_value: int | None = None


# ─── Health ──────────────────────────────────────────────


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": "Wealify Smart Finance",
        "version": "3.1.0",
        "mode": "dashboard",
        "demo_mode": DEMO_MODE,
        "has_api_key": bool(BYTEPLUS_API_KEY),
        "disclaimer": DISCLAIMER_VI,
    }


# ─── Findings API (PDF-compliant output) ────────────────


@app.get("/findings")
def get_findings():
    """
    Generate all findings in PDF-compliant schema (Mục 5.1).
    This is the primary output for evaluate.py scoring.
    """
    findings = generate_all_findings(
        _data["account_statement"],
        _data["card_statement"],
        _data["wallet_balance"],
        _data["emails"],
    )
    return {
        "total": len(findings),
        "findings": findings,
    }


# ─── Audit Log API ──────────────────────────────────────


@app.get("/audit-log/export")
def export_audit_log():
    """Export audit log as JSON file."""
    filepath = audit_log.export_flags()
    return {
        "status": "exported",
        "total_flags": len(audit_log.entries),
        "exported_to": filepath,
    }


# ─── Dashboard API endpoints ────────────────────────────


@app.get("/dashboard/overview")
def dashboard_overview():
    """Financial overview: totals, monthly breakdown, top charges."""
    analysis = analyze_statement(_data["account_statement"], "vi")
    return {
        "summary": analysis["summary"],
        "monthly_breakdown": analysis["monthly_breakdown"],
        "top3_largest": analysis["top3_largest"],
        "categories": analysis["categories"],
    }


@app.get("/dashboard/transactions")
def dashboard_transactions():
    """Full transaction list for table view."""
    return {
        "account_transactions": _data["account_statement"],
        "card_transactions": _data["card_statement"],
        "total_account": len(_data["account_statement"]),
        "total_card": len(_data["card_statement"]),
    }


@app.get("/dashboard/anomalies")
def dashboard_anomalies():
    """Subscriptions, price hikes, duplicates, unknown merchants."""
    return detect_anomalies(_data["account_statement"], "vi")


@app.get("/dashboard/reconciliation")
def dashboard_reconciliation():
    """3-source reconciliation: account ↔ card ↔ wallet."""
    return reconcile_three_sources(
        _data["account_statement"],
        _data["card_statement"],
        _data["wallet_balance"],
        "vi",
    )


@app.get("/dashboard/email-matches")
def dashboard_email_matches():
    """Email-to-transaction matching results."""
    matches = match_transactions_to_emails(
        _data["account_statement"],
        _data["emails"],
        "vi",
    )
    summary = get_match_summary(matches, "vi")
    return {
        "matches": matches,
        "summary": summary,
    }


@app.get("/dashboard/risk-score")
def dashboard_risk_score():
    """Overall risk score 0-100 with breakdown."""
    anomalies = detect_anomalies(_data["account_statement"], "vi")
    reconciliation = reconcile_three_sources(
        _data["account_statement"],
        _data["card_statement"],
        _data["wallet_balance"],
        "vi",
    )
    email_matches = match_transactions_to_emails(
        _data["account_statement"],
        _data["emails"],
        "vi",
    )
    return calculate_risk_score(anomalies, reconciliation, email_matches)


@app.get("/dashboard/report")
def dashboard_report():
    """Full financial report."""
    analysis = analyze_statement(_data["account_statement"], "vi")
    anomalies = detect_anomalies(_data["account_statement"], "vi")
    return generate_report(analysis, anomalies, "vi")


_REPORT_CATEGORY_LABELS_VI = {
    "top_up": "Nạp tiền",
    "withdrawal": "Rút tiền",
    "adjustment": "Điều chỉnh",
    "refund": "Hoàn tiền",
}


def _report_year() -> int:
    years = []
    for t in _data["account_statement"]:
        date = str(t.get("date", ""))
        if len(date) >= 4 and date[:4].isdigit():
            years.append(int(date[:4]))
    return max(years) if years else datetime.utcnow().year


def _normalize_report_type(type_value: str) -> str | None:
    t = (type_value or "").strip().lower()
    mapping = {
        "top_up": "top_up",
        "topup": "top_up",
        "payin": "top_up",
        "transfer": "top_up",
        "withdrawal": "withdrawal",
        "withdraw": "withdrawal",
        "payout": "withdrawal",
        "adjustment": "adjustment",
        "refund": "refund",
    }
    return mapping.get(t)


def _is_success_status(status_value: str | None) -> bool:
    if status_value is None:
        return True
    return str(status_value).strip().lower() == "success"


def _extract_report_transactions(year: int, month: int | None = None) -> list[dict]:
    out = []
    raw = _data.get("_wealify_raw", {})
    va_transactions = raw.get("va_transactions") if isinstance(raw, dict) else None
    vc_transactions = raw.get("vc_transactions") if isinstance(raw, dict) else None

    if isinstance(va_transactions, list) or isinstance(vc_transactions, list):
        for txn in (va_transactions or []):
            if not _is_success_status(txn.get("va_transaction_status")):
                continue
            date = str(txn.get("created_at", ""))[:10]
            if not (len(date) >= 7 and date[:4].isdigit() and date[5:7].isdigit()):
                continue
            y = int(date[:4])
            m = int(date[5:7])
            if y != year or (month is not None and m != month):
                continue

            category_key = _normalize_report_type(str(txn.get("transaction_type", "")))
            if category_key is None:
                continue

            amount_raw = float(txn.get("amount", 0.0) or 0.0)
            amount_abs = abs(amount_raw)
            if category_key == "top_up":
                money_in, money_out = amount_abs, 0.0
            elif category_key == "withdrawal":
                money_in, money_out = 0.0, amount_abs
            else:
                money_in, money_out = (amount_abs, 0.0) if amount_raw >= 0 else (0.0, amount_abs)

            currency = txn.get("currency_symbol") or "VND"
            out.append(
                {
                    "date": date,
                    "currency": currency,
                    "category_key": category_key,
                    "category_label": _REPORT_CATEGORY_LABELS_VI[category_key],
                    "amount_abs": amount_abs,
                    "money_in": money_in,
                    "money_out": money_out,
                }
            )

        for txn in vc_transactions:
            if not _is_success_status(txn.get("transaction_vc_status")):
                continue
            date = str(txn.get("created_at", ""))[:10]
            if not (len(date) >= 7 and date[:4].isdigit() and date[5:7].isdigit()):
                continue
            y = int(date[:4])
            m = int(date[5:7])
            if y != year or (month is not None and m != month):
                continue

            category_key = _normalize_report_type(str(txn.get("transaction_vc_type", "")))
            if category_key is None:
                continue

            amount_raw = float(txn.get("amount", 0.0) or 0.0)
            amount_abs = abs(amount_raw)
            if category_key in ("top_up", "refund"):
                money_in = amount_abs
                money_out = 0.0
            elif category_key == "withdrawal":
                money_in = 0.0
                money_out = amount_abs
            else:  # adjustment
                if amount_raw >= 0:
                    money_in = amount_abs
                    money_out = 0.0
                else:
                    money_in = 0.0
                    money_out = amount_abs

            currency = "USD"
            if isinstance(txn.get("currency"), dict):
                currency = txn["currency"].get("symbol", "USD")

            out.append(
                {
                    "date": date,
                    "currency": currency,
                    "category_key": category_key,
                    "category_label": _REPORT_CATEGORY_LABELS_VI[category_key],
                    "amount_abs": amount_abs,
                    "money_in": money_in,
                    "money_out": money_out,
                }
            )
        return out

    # Fallback for non-live/mock mode
    for txn in _data["account_statement"]:
        date = str(txn.get("date", ""))
        if not (len(date) >= 7 and date[:4].isdigit() and date[5:7].isdigit()):
            continue
        y = int(date[:4])
        m = int(date[5:7])
        if y != year or (month is not None and m != month):
            continue
        if not _is_success_status(txn.get("status")):
            continue

        category_key = _normalize_report_type(str(txn.get("type", "")))
        if category_key is None:
            continue
        amount_raw = float(txn.get("amount", 0.0) or 0.0)
        amount_abs = abs(amount_raw)
        money_in = amount_abs if amount_raw > 0 else 0.0
        money_out = amount_abs if amount_raw < 0 else 0.0
        currency = txn.get("_currency") or "USD"
        out.append(
            {
                "date": date,
                "currency": currency,
                "category_key": category_key,
                "category_label": _REPORT_CATEGORY_LABELS_VI[category_key],
                "amount_abs": amount_abs,
                "money_in": money_in,
                "money_out": money_out,
            }
        )
    return out


def _count_success_transactions(year: int, month: int) -> int:
    raw = _data.get("_wealify_raw", {})
    va_transactions = raw.get("va_transactions") if isinstance(raw, dict) else None
    vc_transactions = raw.get("vc_transactions") if isinstance(raw, dict) else None

    if isinstance(va_transactions, list) or isinstance(vc_transactions, list):
        total = 0
        for txn in (va_transactions or []):
            date = str(txn.get("created_at", ""))[:10]
            if not (len(date) >= 7 and date[:4].isdigit() and date[5:7].isdigit()):
                continue
            y = int(date[:4])
            m = int(date[5:7])
            if y == year and m == month and _is_success_status(txn.get("va_transaction_status")):
                total += 1
        for txn in (vc_transactions or []):
            date = str(txn.get("created_at", ""))[:10]
            if not (len(date) >= 7 and date[:4].isdigit() and date[5:7].isdigit()):
                continue
            y = int(date[:4])
            m = int(date[5:7])
            if y == year and m == month and _is_success_status(txn.get("transaction_vc_status")):
                total += 1
        return total

    # Fallback for non-live/mock mode where explicit status may not exist.
    return len([t for t in _data["account_statement"] if str(t.get("date", "")).startswith(f"{year}-{month:02d}")])


def _money_series_for_year(year: int) -> dict:
    rows = _extract_report_transactions(year)
    totals = {}
    for row in rows:
        cur = row["currency"]
        month_key = row["date"][:7]
        if cur not in totals:
            totals[cur] = {}
        if month_key not in totals[cur]:
            totals[cur][month_key] = {"money_in": 0.0, "money_out": 0.0}
        totals[cur][month_key]["money_in"] += row["money_in"]
        totals[cur][month_key]["money_out"] += row["money_out"]

    result = {}
    for cur, months in totals.items():
        list_rows = []
        for m in range(1, 13):
            month_key = f"{year}-{m:02d}"
            values = months.get(month_key, {"money_in": 0.0, "money_out": 0.0})
            list_rows.append(
                {
                    "month": month_key,
                    "money_in": round(values["money_in"], 2),
                    "money_out": round(values["money_out"], 2),
                }
            )
        result[cur] = list_rows
    return result


def _build_month_report(year: int, month: int) -> dict:
    month_prefix = f"{year}-{month:02d}"
    transactions = _extract_report_transactions(year, month)
    success_total_count = _count_success_transactions(year, month)
    categories_by_currency = {}
    for txn in transactions:
        currency = txn["currency"]
        cat = txn["category_key"]
        if currency not in categories_by_currency:
            categories_by_currency[currency] = {}
        if cat not in categories_by_currency[currency]:
            categories_by_currency[currency][cat] = {
                "category_key": cat,
                "category_label": txn["category_label"],
                "total_amount": 0.0,
                "transaction_count": 0,
            }
        categories_by_currency[currency][cat]["total_amount"] += txn["amount_abs"]
        categories_by_currency[currency][cat]["transaction_count"] += 1

    money_summary_by_currency = {}
    normalized = {}
    for currency, cat_map in categories_by_currency.items():
        normalized[currency] = sorted(
            [
                {
                    **row,
                    "total_amount": round(row["total_amount"], 2),
                }
                for row in cat_map.values()
            ],
            key=lambda r: r["total_amount"],
            reverse=True,
        )
        money_in = sum(t["money_in"] for t in transactions if t["currency"] == currency)
        money_out = sum(t["money_out"] for t in transactions if t["currency"] == currency)
        money_summary_by_currency[currency] = {
            "money_in": round(money_in, 2),
            "money_out": round(money_out, 2),
        }

    return {
        "period_type": "month",
        "year": year,
        "month": month,
        "month_key": month_prefix,
        "success_total_count": success_total_count,
        "success_in_report_count": len(transactions),
        "currencies": sorted(normalized.keys()),
        "categories_by_currency": normalized,
        "money_summary_by_currency": money_summary_by_currency,
        "text_summary": (
            f"Tháng {month}/{year} có {success_total_count} giao dịch SUCCESS, "
            f"trong đó {len(transactions)} giao dịch thuộc 4 loại báo cáo: "
            "nạp tiền, rút tiền, điều chỉnh, hoàn tiền."
        ),
    }


def _build_quarter_report(year: int, quarter: int) -> dict:
    monthly = _money_series_for_year(year)
    month_start = (quarter - 1) * 3 + 1
    month_end = month_start + 2
    month_keys = [f"{year}-{m:02d}" for m in range(month_start, month_end + 1)]

    by_currency = {}
    for currency, rows in monthly.items():
        selected = [row for row in rows if row["month"] in month_keys]
        by_currency[currency] = selected

    return {
        "period_type": "quarter",
        "year": year,
        "quarter": quarter,
        "month_keys": month_keys,
        "currencies": sorted(by_currency.keys()),
        "comparison_by_currency": by_currency,
        "text_summary": (
            f"Quý {quarter}/{year} so sánh tiền vào và tiền ra theo từng tháng."
        ),
    }


def _build_year_report(year: int) -> dict:
    monthly = _money_series_for_year(year)
    return {
        "period_type": "year",
        "year": year,
        "currencies": sorted(monthly.keys()),
        "comparison_by_currency": monthly,
        "text_summary": (
            f"Báo cáo năm {year} so sánh 12 tháng theo tiền vào và tiền ra."
        ),
    }


def _render_report_email_body(report: dict) -> str:
    period_type = report.get("period_type")
    if period_type == "month":
        month = report.get("month")
        year = report.get("year")
        lines = [
            f"Báo cáo tháng {month}/{year}",
            "",
            report.get("text_summary", ""),
            "",
        ]
        categories = report.get("categories_by_currency", {})
        for currency, rows in categories.items():
            lines.append(f"[{currency}]")
            for row in rows:
                lines.append(
                    f"- {row['category_label']}: {row['total_amount']:,.2f} ({row['transaction_count']} giao dịch)"
                )
            money = report.get("money_summary_by_currency", {}).get(currency, {})
            lines.append(f"- Tổng tiền vào: {money.get('money_in', 0):,.2f}")
            lines.append(f"- Tổng tiền ra: {money.get('money_out', 0):,.2f}")
            lines.append("")
        lines.append(DISCLAIMER_VI)
        return "\n".join(lines)

    if period_type == "quarter":
        quarter = report.get("quarter")
        year = report.get("year")
        lines = [
            f"Báo cáo quý {quarter}/{year}",
            "",
            report.get("text_summary", ""),
            "",
        ]
        for currency, rows in report.get("comparison_by_currency", {}).items():
            lines.append(f"[{currency}]")
            for row in rows:
                lines.append(
                    f"- {row['month']}: Tiền vào {row['money_in']:,.2f} | Tiền ra {row['money_out']:,.2f}"
                )
            lines.append("")
        lines.append(DISCLAIMER_VI)
        return "\n".join(lines)

    year = report.get("year")
    lines = [
        f"Báo cáo năm {year}",
        "",
        report.get("text_summary", ""),
        "",
    ]
    for currency, rows in report.get("comparison_by_currency", {}).items():
        lines.append(f"[{currency}]")
        for row in rows:
            lines.append(
                f"- {row['month']}: Tiền vào {row['money_in']:,.2f} | Tiền ra {row['money_out']:,.2f}"
            )
        lines.append("")
    lines.append(DISCLAIMER_VI)
    return "\n".join(lines)


@app.get("/dashboard/reporting/meta")
def dashboard_reporting_meta():
    year = _report_year()
    return {
        "year": year,
        "months": list(range(1, 13)),
        "quarters": [1, 2, 3, 4],
    }


@app.get("/dashboard/reporting/month/{month}")
def dashboard_reporting_month(month: int):
    if month < 1 or month > 12:
        return {"status": "invalid_month", "message": "month must be 1..12"}
    year = _report_year()
    return _build_month_report(year, month)


@app.get("/dashboard/reporting/quarter/{quarter}")
def dashboard_reporting_quarter(quarter: int):
    if quarter < 1 or quarter > 4:
        return {"status": "invalid_quarter", "message": "quarter must be 1..4"}
    year = _report_year()
    return _build_quarter_report(year, quarter)


@app.get("/dashboard/reporting/year")
def dashboard_reporting_year():
    year = _report_year()
    return _build_year_report(year)


@app.post("/dashboard/reporting/send-email")
def dashboard_reporting_send_email(req: ReportEmailRequest):
    period_type = req.period_type.strip().lower()

    if period_type == "month":
        if req.period_value is None or req.period_value < 1 or req.period_value > 12:
            return {"status": "invalid_month", "message": "period_value must be 1..12 for month"}
        report = dashboard_reporting_month(req.period_value)
        subject = f"Wealify báo cáo tháng {req.period_value}/{report['year']}"
    elif period_type == "quarter":
        if req.period_value is None or req.period_value < 1 or req.period_value > 4:
            return {"status": "invalid_quarter", "message": "period_value must be 1..4 for quarter"}
        report = dashboard_reporting_quarter(req.period_value)
        subject = f"Wealify báo cáo quý {req.period_value}/{report['year']}"
    elif period_type == "year":
        report = dashboard_reporting_year()
        subject = f"Wealify báo cáo năm {report['year']}"
    else:
        return {"status": "invalid_period_type", "message": "period_type must be month|quarter|year"}

    from email_sender import send_email, is_configured, EmailSendError

    body = _render_report_email_body(report)

    if not is_configured():
        return {
            "status": "email_send_failed",
            "to": USER_EMAIL,
            "reason": "SMTP chưa được cấu hình",
            "subject": subject,
            "body": body,
        }

    try:
        send_email(USER_EMAIL, subject, body)
    except EmailSendError as e:
        return {
            "status": "email_send_failed",
            "to": USER_EMAIL,
            "reason": str(e),
            "subject": subject,
            "body": body,
        }

    return {
        "status": "sent",
        "to": USER_EMAIL,
        "subject": subject,
    }


@app.get("/dashboard/reports")
def dashboard_reports_index():
    """List which monthly/yearly reports are cached in backend/report/."""
    return report_cache.list_cached_keys(datetime.utcnow().year)


@app.get("/dashboard/reports/{key}")
def dashboard_reports_get(key: str):
    """
    Fetch a pre-generated report from cache: key is "YYYY-MM" for a single
    month or "YYYY" for the yearly aggregate. Nhiệm vụ 6: pre-generated by
    a background job, only the current month gets regenerated when newer
    data appears (see report_cache.py).
    """
    cached = report_cache.get_cached_report(key)
    if cached is None:
        return {"status": "not_generated", "key": key}
    return cached


# ─── Nhiệm vụ 7: configurable deadline reminders ────────


@app.get("/settings/reminder-config")
def get_reminder_config():
    """Current threshold settings (hours) for the 2 reminder situations."""
    return reminder_checker.load_reminder_config()


@app.post("/settings/reminder-config")
def set_reminder_config(req: ReminderConfigRequest):
    """Save threshold settings (hours) for the 2 reminder situations."""
    return reminder_checker.save_reminder_config(req.dict())


@app.get("/dashboard/reminders")
def dashboard_reminders():
    """
    Nhiệm vụ 7 — 2 situations, each triggered past its configured
    threshold: (1) an inbound-payment email not yet cleanly resolved on
    Wealify (no match / still processing / amount mismatch / failed),
    (2) a real Wealify transaction (card or VA) stuck in
    PENDING/PROCESSING/WAITING status.
    """
    cfg = reminder_checker.load_reminder_config()
    va_transactions = _data.get("_wealify_raw", {}).get("va_transactions", [])

    stale_processing = reminder_checker.check_stale_processing_transactions(
        _data["card_statement"], cfg["processing_status_hours"], "vi"
    ) + reminder_checker.check_stale_va_transactions(
        va_transactions, cfg["processing_status_hours"], "vi"
    )
    stale_inbound = reminder_checker.check_stale_unverified_inbound_emails(
        _data["emails"], va_transactions, cfg["inbound_email_hours"], "vi"
    )
    return {
        "config": cfg,
        "stale_processing_transactions": stale_processing,
        "stale_unverified_inbound_emails": stale_inbound,
        "total": len(stale_processing) + len(stale_inbound),
    }


@app.get("/dashboard/wallet")
def dashboard_wallet():
    """Current wallet/balance info."""
    return _data["wallet_balance"]


def _run_scheduled_check() -> dict:
    """
    Refresh data from source (mock or live Wealify, per USE_LIVE_WEALIFY),
    re-scan with all agents, and log only genuinely new flags — audit_log's
    dedup skips anything already reported. This is the one place that
    re-fetches data, so both the manual endpoint and the background loop
    can actually see transactions that appeared since the last check.
    Meets WLF-01 requirement: 'chạy định kỳ không báo trùng'.
    Never sends email on its own — self-notify still requires confirmation.
    """
    global _data
    _data = get_all_data()

    anomalies = detect_anomalies(_data["account_statement"], "vi")

    # Only regenerates the current month's cached report (+ yearly total)
    # when a transaction newer than the cache actually appeared — cheap
    # no-op on every other run.
    report_cache.refresh_current_month_if_stale(_data["account_statement"], anomalies, "vi")

    recon = reconcile_three_sources(
        _data["account_statement"],
        _data["card_statement"],
        _data["wallet_balance"],
        "vi",
    )
    email_matches = match_transactions_to_emails(
        _data["account_statement"],
        _data["emails"],
        "vi",
    )
    risk = calculate_risk_score(anomalies, recon, email_matches)

    new_flags = 0
    total_issues = 0

    # Flag anomalies
    for u in anomalies.get("unknown_merchants", []):
        total_issues += 1
        if audit_log.log_flag(u["reference"], "unknown_merchant", "medium",
                              "Cần bạn tự xác nhận", "anomaly_detector",
                              u.get("explanation", "")):
            new_flags += 1

    for d in anomalies.get("duplicate_charges", []):
        total_issues += 1
        if audit_log.log_flag(d["reference"], "duplicate_charge", "high",
                              "Cần bạn tự xác nhận", "anomaly_detector",
                              f"Duplicate of {d.get('duplicate_of', '')}"):
            new_flags += 1

    for h in anomalies.get("price_hikes", []):
        total_issues += 1
        # Ref includes the specific old→new prices, not just the merchant
        # name — otherwise a merchant's *second* (different) price hike
        # would be silently deduped forever against its first.
        ref = f"{h['merchant']}|{h['old_price']}->{h['new_price']}"
        if audit_log.log_flag(ref, "price_hike", "high",
                              "Cần bạn tự xác nhận", "anomaly_detector",
                              f"${h['old_price']} → ${h['new_price']}"):
            new_flags += 1

    for disc in recon.get("discrepancies", []):
        total_issues += 1
        disc_type = disc.get("type", "discrepancy")
        # Aggregate checks like wallet_card_mismatch have no per-transaction
        # reference — fold the magnitude into the ref so a changed/worsened
        # mismatch is treated as new, not deduped against the first sighting.
        # Explicit key-presence check, not `or`: reconciler.py can
        # legitimately produce reference="" for some discrepancy types
        # (traced back to an empty transaction_id), and a falsy check would
        # wrongly treat that as "no reference" and change its dedup identity.
        if "reference" in disc:
            ref = disc["reference"]
        else:
            ref = f"{disc_type}|{disc.get('difference', disc.get('detail', ''))}"
        if audit_log.log_flag(ref, disc_type, "medium",
                              "Cần bạn tự xác nhận", "reconciler",
                              disc.get("detail", "")):
            new_flags += 1

    for m in email_matches:
        if m.get("match_status") == "suspicious_email":
            total_issues += 1
            if audit_log.log_flag(m["reference"], "suspicious_email", "high",
                                  "Cần bạn tự xác nhận", "email_matcher",
                                  "; ".join(m.get("suspicious_reasons", []))):
                new_flags += 1

    return {
        "status": "completed",
        "risk_score": risk,
        "total_issues": total_issues,
        "new_flags": new_flags,
        "already_reported": total_issues - new_flags,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


async def _periodic_check_loop():
    """Background task: run the scheduled check every SCHEDULED_CHECK_INTERVAL_SECONDS."""
    while True:
        await asyncio.sleep(SCHEDULED_CHECK_INTERVAL_SECONDS)
        try:
            result = await asyncio.to_thread(_run_scheduled_check)
            logger.info(
                "[periodic-check] %d new flags (%d already reported)",
                result["new_flags"], result["already_reported"],
            )
        except Exception as e:
            logger.warning("[periodic-check] failed: %s", e)


@app.post("/scheduled-check")
def scheduled_check():
    """Manually trigger the same check the background loop runs periodically."""
    return _run_scheduled_check()


# ─── AI Insight endpoint ────────────────────────────────


@app.post("/ai/insight")
def ai_insight(req: InsightRequest):
    """
    Generate AI insight using BytePlus ModelArk — DeepSeek V4 Flash.
    Falls back to cached insight if no API key.
    """
    analysis = analyze_statement(_data["account_statement"], "vi")
    anomalies = detect_anomalies(_data["account_statement"], "vi")
    reconciliation = reconcile_three_sources(
        _data["account_statement"],
        _data["card_statement"],
        _data["wallet_balance"],
        "vi",
    )

    # Build context for LLM
    summary = analysis["summary"]
    note = income_note("vi")
    n_anomalies = anomalies.get("total_anomalies", 0)
    n_subs = len(anomalies.get("subscriptions", []))
    n_hikes = len(anomalies.get("price_hikes", []))
    n_disc = reconciliation.get("total_discrepancies", 0)

    if BYTEPLUS_API_KEY:
        try:
            from llm_client import call_llm

            note_line = f"({note})\n" if note else ""
            prompt = f"""Phân tích tài chính ngắn gọn cho seller cross-border, dựa trên dữ liệu:

Tổng quan:
{_dict_to_text(summary)}
{note_line}
Phát hiện:
- {n_anomalies} khoản bất thường
- {n_subs} gói đăng ký đang hoạt động
- {n_hikes} gói tăng giá âm thầm
- {n_disc} khoản lệch giữa 3 nguồn (tài khoản, thẻ, ví)

Top 3 khoản lớn nhất:
{_format_top3(analysis.get('top3_largest', []))}

Gói tăng giá:
{_format_hikes(anomalies.get('price_hikes', []))}

Yêu cầu:
1. Tóm tắt tình hình tài chính trong 2-3 câu
2. Đưa ra 3 gợi ý hành động cụ thể, có số liệu
3. Cảnh báo rủi ro nếu có
4. Giọng văn: chuyên nghiệp, thân thiện, gần gũi với seller
5. KHÔNG phóng đại, KHÔNG hứa hẹn, KHÔNG kết luận tuyệt đối
"""
            system = (
                "You are Wealify — an AI financial assistant for cross-border e-commerce sellers. "
                "Respond in Vietnamese. Be concise, actionable, and data-driven. "
                "Never make definitive safety claims. Always say 'khuyến nghị' not 'phải làm'."
            )
            # DeepSeek V4 Flash is a reasoning model — its "thinking" tokens
            # count against this budget before the final answer, so keep
            # plenty of headroom or replies get cut off mid-thought.
            insight_text = call_llm(prompt, system=system, max_tokens=1500)
            return {
                "insight": insight_text,
                "source": "byteplus_deepseek_v4_flash",
                "powered_by": "BytePlus ModelArk — DeepSeek V4 Flash",
            }
        except Exception as e:
            print(f"[AI] LLM call failed: {e}, using cached insight")

    # Fallback: cached/generated insight
    insight = _generate_cached_insight(summary, anomalies, reconciliation)
    return {
        "insight": insight,
        "source": "cached",
        "powered_by": "BytePlus ModelArk — DeepSeek V4 Flash (demo mode)",
    }


# ─── Chat endpoint (kept for Tab 4) ─────────────────────


@app.post("/chat")
def chat(req: ChatRequest):
    """Chat endpoint — process user message and return response."""
    result = orchestrator.process_message(req.message)
    return result


@app.get("/audit-log")
def get_audit_log():
    """Get all audit log entries."""
    return {
        "entries": audit_log.get_all_flags(),
        "summary": audit_log.get_summary(),
    }


@app.post("/reset")
def reset_session():
    """Reset chat session (for demo purposes)."""
    global orchestrator, _data
    orchestrator = ChatOrchestrator()
    _data = get_all_data()
    audit_log.clear()
    return {"status": "reset", "message": "Session and data reloaded."}


# ─── Helpers ──────────────────────────────────────────────


def _dict_to_text(summary_by_currency: dict) -> str:
    """summary_by_currency is {currency: {label: value}} — statement mixes
    VND/USD/EUR, so each currency's totals are listed separately, never summed."""
    lines = []
    for currency, d in summary_by_currency.items():
        lines.append(f"[{currency}]")
        lines.extend(f"- {k}: {v}" for k, v in d.items())
    return "\n".join(lines)


def _format_top3(items_by_currency: dict) -> str:
    if not items_by_currency:
        return "Không có dữ liệu"
    lines = []
    for currency, items in items_by_currency.items():
        symbol = CURRENCY_SYMBOLS.get(currency, currency + " ")
        for i, t in enumerate(items, 1):
            lines.append(f"{i}. [{currency}] {t['description']} — {symbol}{abs(t['amount']):,.2f} ({t['date']})")
    return "\n".join(lines) if lines else "Không có dữ liệu"


def _format_hikes(hikes: list) -> str:
    if not hikes:
        return "Không có gói nào tăng giá"
    lines = []
    for h in hikes:
        lines.append(
            f"- {h['merchant']}: ${h['old_price']} → ${h['new_price']} "
            f"(+{h['increase_pct']}%)"
        )
    return "\n".join(lines)


def _generate_cached_insight(summary, anomalies, reconciliation) -> str:
    """Generate a smart cached insight from data."""
    n_anomalies = anomalies.get("total_anomalies", 0)
    subs = anomalies.get("subscriptions", [])
    hikes = anomalies.get("price_hikes", [])
    discs = reconciliation.get("total_discrepancies", 0)

    parts = []

    # Financial summary — summary is {currency: {label: value}}; report each
    # currency separately since the statement mixes VND/USD/EUR with no conversion.
    for currency, group in summary.items():
        total_in = 0
        total_out = 0
        for k, v in group.items():
            if "vào" in k.lower() or "income" in k.lower():
                total_in = v
            if "chi tiêu" in k.lower() or "spending" in k.lower():
                total_out = v

        if total_in and total_out:
            symbol = CURRENCY_SYMBOLS.get(currency, currency + " ")
            ratio = total_out / total_in * 100 if total_in else 0
            parts.append(
                f"📊 **Tổng quan ({currency}):** Tháng này bạn chi {symbol}{total_out:,.2f} "
                f"trên tổng thu {symbol}{total_in:,.2f} ({ratio:.0f}% thu nhập)."
            )

    # Subscriptions
    if subs:
        total_monthly = sum(s["current_price"] for s in subs if s.get("frequency") == "monthly")
        parts.append(
            f"📋 **Gói đăng ký:** {len(subs)} gói đang hoạt động, "
            f"tổng ${total_monthly:,.2f}/tháng."
        )

    # Price hikes
    if hikes:
        hike_names = ", ".join(h["merchant"] for h in hikes[:3])
        parts.append(
            f"⚠️ **Tăng giá:** {len(hikes)} gói tăng giá âm thầm ({hike_names}). "
            f"Khuyến nghị xem xét huỷ nếu không sử dụng."
        )

    # Discrepancies
    if discs > 0:
        parts.append(
            f"🔍 **Đối chiếu:** Phát hiện {discs} khoản lệch giữa tài khoản, thẻ và ví. "
            f"Khuyến nghị kiểm tra chi tiết ở tab Đối chiếu."
        )

    # Anomalies
    if n_anomalies > 0:
        parts.append(
            f"🚨 **Cảnh báo:** {n_anomalies} khoản cần kiểm tra "
            f"(khoản lạ, trùng lặp, hoặc không có email xác nhận)."
        )

    if not parts:
        parts.append("✅ Tài khoản hoạt động bình thường, chưa phát hiện bất thường đáng kể.")

    parts.append(
        "\n\n💡 **Gợi ý:** Kiểm tra các tab Đối chiếu và An toàn để xem chi tiết. "
        "Nếu có khoản lạ, hãy liên hệ ngân hàng/Wealify trong thời hạn 60 ngày."
    )

    return "\n\n".join(parts)


# ─── Wealify Live API endpoints ─────────────────────────


@app.get("/dashboard/wealify-accounts")
def dashboard_wealify_accounts():
    """
    Live VA/VC accounts from Wealify API.
    Falls back to empty data if API is not configured.
    """
    try:
        from wealify_client import get_wealify_client
        from wealify_adapter import _mask_last4

        client = get_wealify_client()
        va_accounts = client.get_va_list()
        vc_cards = client.get_vc_list()
        wallets = client.get_wallets_balance()
        user_info = client.get_user_info()

        return {
            "status": "live",
            "user": user_info,
            "va_accounts": [
                {
                    "id": va.get("id"),
                    "name": va.get("card_holder", va.get("nickname", "")),
                    "account_number": _mask_last4(va.get("card_number", "")),
                    "bank": va.get("bank", ""),
                    "platform": va.get("platform", {}).get("name", "") if isinstance(va.get("platform"), dict) else str(va.get("platform", "")),
                    "total_received": va.get("total_received", 0),
                    "currency": va.get("currency_symbol", va.get("currency", {}).get("symbol", "VND") if isinstance(va.get("currency"), dict) else "VND"),
                    "status": va.get("status", ""),
                    "created_at": va.get("created_at", ""),
                }
                for va in va_accounts
            ],
            "vc_cards": [
                {
                    "id": vc.get("id"),
                    "name": vc.get("card_name", ""),
                    "last_four": vc.get("last_four", ""),
                    "provider": vc.get("card_provider", ""),
                    "status": vc.get("card_status", ""),
                    "balance": float(vc.get("balance", "0")),
                    "total_top_up": float(vc.get("total_top_up", "0")),
                    "total_withdraw": float(vc.get("total_withdraw", "0")),
                    "category": vc.get("category", ""),
                    "expiry_date": vc.get("expiry_date", ""),
                }
                for vc in vc_cards
            ],
            "wallets": wallets,
            "summary": {
                "total_va": len(va_accounts),
                "total_vc": len(vc_cards),
                "active_va": sum(1 for va in va_accounts if va.get("status") == "ACTIVE"),
                "active_vc": sum(1 for vc in vc_cards if vc.get("card_status") == "ACTIVE"),
            },
            "powered_by": "Wealify × BytePlus ModelArk — DeepSeek V4 Flash",
        }
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
            "message": "Wealify API not configured. Set WEALIFY_EMAIL and WEALIFY_PASSWORD in .env",
            "va_accounts": [],
            "vc_cards": [],
            "wallets": [],
        }


@app.get("/dashboard/wealify-transactions")
def dashboard_wealify_transactions():
    """
    VC card transactions from Wealify API.
    VA transactions endpoint returns 500 on dev, so we use VC transactions.
    """
    try:
        from wealify_client import get_wealify_client

        client = get_wealify_client()
        vc_txns = client.get_vc_transactions()

        transactions = [
            {
                "date": txn.get("created_at", ""),
                "reference": txn.get("transaction_id", ""),
                "type": txn.get("transaction_vc_type", ""),
                "detail_type": txn.get("vc_detail_transaction_type", ""),
                "amount": txn.get("amount", 0),
                "currency": txn.get("currency", {}).get("symbol", "USD") if isinstance(txn.get("currency"), dict) else "USD",
                "status": txn.get("transaction_vc_status", ""),
                "remark": txn.get("remark", ""),
                "card_name": txn.get("_card_name", ""),
                "card_last4": txn.get("_card_last4", ""),
            }
            for txn in vc_txns
        ]

        return {
            "status": "live",
            "total": len(transactions),
            "transactions": transactions,
            "powered_by": "Wealify × BytePlus ModelArk — DeepSeek V4 Flash",
        }
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
            "transactions": [],
        }


@app.get("/dashboard/outbound-reconciliation")
def dashboard_outbound_reconciliation():
    """
    Luồng Tiền ra: match card-payment receipt emails (Gmail) against real
    Wealify VC transactions by the "Ref: CD-XXXX" printed in each email.
    """
    try:
        from gmail_client import fetch_emails
        from wealify_client import get_wealify_client
        from agents.outbound_reconciler import match_outbound_emails
        from config import WEALIFY_EMAIL

        emails = fetch_emails()
        if WEALIFY_EMAIL:
            emails = [e for e in emails if e.get("to") == WEALIFY_EMAIL]

        client = get_wealify_client()
        vc_txns = client.get_vc_transactions()

        result = match_outbound_emails(emails, vc_txns, lang="vi")
        result["status"] = "live"
        return result
    except Exception as e:
        return {"status": "unavailable", "error": str(e), "items": []}


@app.get("/dashboard/suspicious-domains")
def dashboard_suspicious_domains():
    """
    Scan every email (not just ones with a Ref) against the user's domain
    whitelist for lookalike-domain impersonation attempts.
    """
    try:
        from gmail_client import fetch_emails
        from agents.outbound_reconciler import check_suspicious_domains
        from domain_whitelist import get_whitelist
        from config import WEALIFY_EMAIL

        emails = fetch_emails()
        if WEALIFY_EMAIL:
            emails = [e for e in emails if e.get("to") == WEALIFY_EMAIL]

        flags = check_suspicious_domains(emails, get_whitelist(), lang="vi")
        return {"status": "live", "total_flagged": len(flags), "items": flags}
    except Exception as e:
        return {"status": "unavailable", "error": str(e), "items": []}


@app.get("/dashboard/inbound-reconciliation")
def dashboard_inbound_reconciliation():
    """
    Luồng Tiền vào: check bank-payout emails (Gmail) against real Wealify
    VA transactions (GET /v2/transactions/va — confirmed working, unlike
    the broken GET /v2/virtual-accounts/transactions).
    """
    try:
        from gmail_client import fetch_emails
        from agents.inbound_reconciler import check_inbound_emails
        from config import WEALIFY_EMAIL

        emails = fetch_emails()
        if WEALIFY_EMAIL:
            emails = [e for e in emails if e.get("to") == WEALIFY_EMAIL]

        va_transactions = _data.get("_wealify_raw", {}).get("va_transactions", [])
        result = check_inbound_emails(emails, va_transactions, lang="vi")
        result["status"] = "live"
        return result
    except Exception as e:
        return {"status": "unavailable", "error": str(e), "items": []}


# ─── Serve Frontend ─────────────────────────────────────

FRONTEND_DIR = Path(__file__).parent.parent / "frontend-web"


@app.get("/")
def serve_frontend():
    """Serve the HTML frontend."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/setup")
def serve_setup_wizard():
    """Serve the Setup Wizard (Gmail/Wealify credentials + domain whitelist)."""
    return FileResponse(FRONTEND_DIR / "setup.html")


@app.get("/reminders")
def serve_reminder_settings():
    """Serve the Nhiệm vụ 7 reminder-threshold config page."""
    return FileResponse(FRONTEND_DIR / "reminders.html")


app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
