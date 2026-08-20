"""
Agent 6: Email Drafter — Soạn email báo cáo cho người dùng.
Chỉ soạn nháp, KHÔNG tự gửi — chờ user xác nhận.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from config import USER_EMAIL, DISCLAIMER_VI


def draft_report_email(
    report: dict[str, Any],
    anomaly_results: dict[str, Any],
    reconciliation: dict[str, Any],
    lang: str = "vi",
) -> dict[str, Any]:
    """
    Draft a financial report email.
    Returns the draft — does NOT send it.
    """
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    if lang == "en":
        subject = f"Wealify Finance Review — {now}"
        body = _build_email_body_en(report, anomaly_results, reconciliation)
    else:
        subject = f"Wealify Báo cáo Tài chính — {now}"
        body = _build_email_body_vi(report, anomaly_results, reconciliation)

    return {
        "to": USER_EMAIL,
        "subject": subject,
        "body": body,
        "status": "draft",
        "requires_confirmation": True,
        "message": "Email đã soạn xong. Bạn xác nhận gửi không?" if lang == "vi"
                   else "Email draft ready. Confirm to send?",
    }


def draft_dispute_reminder_email(
    items: list[dict[str, Any]],
    lang: str = "vi",
) -> dict[str, Any]:
    """Draft an email listing dispute deadlines."""
    now = datetime.utcnow().strftime("%Y-%m-%d")

    if lang == "vi":
        subject = f"Nhắc hạn khiếu nại — {now}"
        lines = ["Các khoản cần lưu ý thời hạn khiếu nại 60 ngày:\n"]
        for item in items:
            lines.append(
                f"• {item.get('description', '')} — ${abs(item.get('amount', 0)):.2f} "
                f"(ngày {item.get('date', '')}) — Hạn khiếu nại: {item.get('dispute_deadline', 'N/A')}"
            )
        lines.append(f"\n{DISCLAIMER_VI}")
        body = "\n".join(lines)
    else:
        subject = f"Dispute Deadline Reminder — {now}"
        lines = ["Items approaching the 60-day dispute deadline:\n"]
        for item in items:
            lines.append(
                f"• {item.get('description', '')} — ${abs(item.get('amount', 0)):.2f} "
                f"({item.get('date', '')}) — Deadline: {item.get('dispute_deadline', 'N/A')}"
            )
        from config import DISCLAIMER_EN
        lines.append(f"\n{DISCLAIMER_EN}")
        body = "\n".join(lines)

    return {
        "to": USER_EMAIL,
        "subject": subject,
        "body": body,
        "status": "draft",
        "requires_confirmation": True,
        "message": "Email nhắc hạn đã soạn xong. Bạn xác nhận gửi không?" if lang == "vi"
                   else "Reminder email draft ready. Confirm to send?",
    }


def _build_email_body_vi(report, anomalies, reconciliation) -> str:
    lines = []
    lines.append("Xin chào,\n")
    lines.append("Đây là báo cáo rà soát tài chính từ Wealify Smart Finance.\n")

    # Overview
    overview = report.get("overview", {})
    lines.append("📊 TỔNG QUAN")
    for k, v in overview.items():
        lines.append(f"  • {k}: {v}")

    # Subscriptions
    subs = report.get("subscriptions", {})
    lines.append("\n📋 GÓI ĐĂNG KÝ")
    for k, v in subs.items():
        lines.append(f"  • {k}: {v}")

    # Price hikes
    hikes = report.get("price_hike_alerts", [])
    if hikes:
        lines.append("\n⚠️ CẢNH BÁO TĂNG GIÁ")
        for h in hikes:
            lines.append(f"  • {h['service']}: ${h['old']} → ${h['new']} ({h['increase']})")

    # Discrepancies
    discs = reconciliation.get("total_discrepancies", 0)
    if discs > 0:
        lines.append(f"\n🔍 PHÁT HIỆN {discs} KHOẢN LỆCH GIỮA 3 NGUỒN")
        for d in reconciliation.get("discrepancies", [])[:5]:
            lines.append(f"  • {d.get('detail', '')}")

    # Anomalies
    total_anomalies = anomalies.get("total_anomalies", 0)
    if total_anomalies > 0:
        lines.append(f"\n🚨 {total_anomalies} KHOẢN CẦN KIỂM TRA")

    lines.append(f"\n---\n{DISCLAIMER_VI}")

    return "\n".join(lines)


def _build_email_body_en(report, anomalies, reconciliation) -> str:
    lines = []
    lines.append("Hello,\n")
    lines.append("Here is your financial review report from Wealify Smart Finance.\n")

    overview = report.get("overview", {})
    lines.append("📊 OVERVIEW")
    for k, v in overview.items():
        lines.append(f"  • {k}: {v}")

    subs = report.get("subscriptions", {})
    lines.append("\n📋 SUBSCRIPTIONS")
    for k, v in subs.items():
        lines.append(f"  • {k}: {v}")

    hikes = report.get("price_hike_alerts", [])
    if hikes:
        lines.append("\n⚠️ PRICE HIKE ALERTS")
        for h in hikes:
            lines.append(f"  • {h['service']}: ${h['old']} → ${h['new']} ({h['increase']})")

    discs = reconciliation.get("total_discrepancies", 0)
    if discs > 0:
        lines.append(f"\n🔍 FOUND {discs} DISCREPANCIES ACROSS 3 SOURCES")
        for d in reconciliation.get("discrepancies", [])[:5]:
            lines.append(f"  • {d.get('detail', '')}")

    from config import DISCLAIMER_EN
    lines.append(f"\n---\n{DISCLAIMER_EN}")

    return "\n".join(lines)
