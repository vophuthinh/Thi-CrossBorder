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
from pydantic import BaseModel

from config import (
    DEMO_MODE,
    DISCLAIMER_VI,
    DISCLAIMER_EN,
    BYTEPLUS_API_KEY,
    SCHEDULED_CHECK_INTERVAL_SECONDS,
)
from chat import ChatOrchestrator
from audit_log import audit_log
from data_loader import get_all_data
from agents.statement_parser import analyze_statement
from agents.anomaly_detector import detect_anomalies
from agents.reconciler import reconcile_three_sources
from agents.email_matcher import match_transactions_to_emails, get_match_summary
from agents.report_generator import generate_report
from agents.risk_scorer import calculate_risk_score
from finding_engine import generate_all_findings

logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_periodic_check_loop())
    yield
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

# --- Preload data (once) ---
_data = get_all_data()

# Global chat orchestrator (per-server session for demo)
orchestrator = ChatOrchestrator()


# ─── Models ──────────────────────────────────────────────


class ChatRequest(BaseModel):
    message: str


class InsightRequest(BaseModel):
    context: str = "general"


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
        if audit_log.log_flag(h["merchant"], "price_hike", "high",
                              "Cần bạn tự xác nhận", "anomaly_detector",
                              f"${h['old_price']} → ${h['new_price']}"):
            new_flags += 1

    for disc in recon.get("discrepancies", []):
        total_issues += 1
        ref = disc.get("reference", disc.get("type", "unknown"))
        if audit_log.log_flag(ref, disc.get("type", "discrepancy"), "medium",
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
    Generate AI insight using BytePlus Seed 2.0.
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
    n_anomalies = anomalies.get("total_anomalies", 0)
    n_subs = len(anomalies.get("subscriptions", []))
    n_hikes = len(anomalies.get("price_hikes", []))
    n_disc = reconciliation.get("total_discrepancies", 0)

    if BYTEPLUS_API_KEY:
        try:
            from llm_client import call_llm

            prompt = f"""Phân tích tài chính ngắn gọn cho seller cross-border, dựa trên dữ liệu:

Tổng quan:
{_dict_to_text(summary)}

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
            insight_text = call_llm(prompt, system=system, max_tokens=800)
            return {
                "insight": insight_text,
                "source": "byteplus_seed_2.0",
                "powered_by": "BytePlus Seed 2.0",
            }
        except Exception as e:
            print(f"[AI] LLM call failed: {e}, using cached insight")

    # Fallback: cached/generated insight
    insight = _generate_cached_insight(summary, anomalies, reconciliation)
    return {
        "insight": insight,
        "source": "cached",
        "powered_by": "BytePlus Seed 2.0 (demo mode)",
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


def _dict_to_text(d: dict) -> str:
    return "\n".join(f"- {k}: {v}" for k, v in d.items())


def _format_top3(items: list) -> str:
    if not items:
        return "Không có dữ liệu"
    lines = []
    for i, t in enumerate(items, 1):
        lines.append(f"{i}. {t['description']} — ${abs(t['amount']):,.2f} ({t['date']})")
    return "\n".join(lines)


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

    # Financial summary
    total_in = 0
    total_out = 0
    for k, v in summary.items():
        if "vào" in k.lower() or "income" in k.lower():
            total_in = v
        if "chi tiêu" in k.lower() or "spending" in k.lower():
            total_out = v

    if total_in and total_out:
        ratio = total_out / total_in * 100 if total_in else 0
        parts.append(
            f"📊 **Tổng quan:** Tháng này bạn chi ${total_out:,.2f} "
            f"trên tổng thu ${total_in:,.2f} ({ratio:.0f}% thu nhập)."
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
            "powered_by": "Wealify × BytePlus Seed 2.0",
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
            "powered_by": "Wealify × BytePlus Seed 2.0",
        }
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
            "transactions": [],
        }


# ─── Serve Frontend ─────────────────────────────────────

FRONTEND_DIR = Path(__file__).parent.parent / "frontend-web"


@app.get("/")
def serve_frontend():
    """Serve the HTML frontend."""
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
