"""
Agent 7: Risk Scorer — Tính Risk Score tổng hợp 0-100.
Dựa trên: anomalies, discrepancies, suspicious emails, price hikes.
"""
from __future__ import annotations

from typing import Any


def calculate_risk_score(
    anomaly_results: dict[str, Any],
    reconciliation: dict[str, Any],
    email_matches: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate overall financial risk score (0-100).
    Higher = more risky.

    Breakdown:
    - Anomalies (max 30): unknown merchants, duplicates
    - Discrepancies (max 25): 3-source mismatches
    - Suspicious emails (max 25): phishing, fake receipts
    - Price hikes (max 20): silent subscription increases
    """
    scores = {}

    # --- Anomaly score (max 30) ---
    # Weights sized so a busy-but-not-catastrophic statement (a handful of
    # unclear merchant names) doesn't already max the category — leaves
    # headroom for the score to actually distinguish severity.
    unknown = len(anomaly_results.get("unknown_merchants", []))
    duplicates = len(anomaly_results.get("duplicate_charges", []))
    anomaly_raw = min(unknown * 2 + duplicates * 3, 30)
    scores["anomalies"] = {
        "score": anomaly_raw,
        "max": 30,
        "detail": f"{unknown} khoản lạ, {duplicates} khoản trùng",
        "detail_en": f"{unknown} unknown merchants, {duplicates} duplicates",
    }

    # --- Discrepancy score (max 25) ---
    disc_count = reconciliation.get("total_discrepancies", 0)
    disc_raw = min(disc_count * 3, 25)
    scores["discrepancies"] = {
        "score": disc_raw,
        "max": 25,
        "detail": f"{disc_count} khoản lệch giữa 3 nguồn",
        "detail_en": f"{disc_count} cross-source discrepancies",
    }

    # --- Suspicious email score (max 25) ---
    # "No matching email" maps to the "Chưa đủ dữ liệu" (insufficient data)
    # label, not a confirmed risk — so it should nudge the score, not drive
    # it. A confirmed suspicious/lookalike email is the real signal here.
    suspicious_count = sum(
        1 for m in email_matches if m.get("match_status") == "suspicious_email"
    )
    no_email_count = sum(
        1 for m in email_matches if m.get("match_status") == "no_email"
    )
    email_raw = min(round(suspicious_count * 15 + no_email_count * 0.5), 25)
    scores["suspicious_emails"] = {
        "score": email_raw,
        "max": 25,
        "detail": f"{suspicious_count} email nghi giả, {no_email_count} không có email",
        "detail_en": f"{suspicious_count} suspicious emails, {no_email_count} no email found",
    }

    # --- Price hike score (max 20) ---
    hike_count = len(anomaly_results.get("price_hikes", []))
    hike_raw = min(hike_count * 8, 20)
    scores["price_hikes"] = {
        "score": hike_raw,
        "max": 20,
        "detail": f"{hike_count} gói tăng giá âm thầm",
        "detail_en": f"{hike_count} silent price increases",
    }

    # --- Total ---
    total = sum(s["score"] for s in scores.values())

    # Risk level
    if total <= 20:
        level = "LOW"
        level_vi = "THẤP"
        color = "#22c55e"
    elif total <= 50:
        level = "MEDIUM"
        level_vi = "TRUNG BÌNH"
        color = "#f59e0b"
    elif total <= 75:
        level = "HIGH"
        level_vi = "CAO"
        color = "#ef4444"
    else:
        level = "CRITICAL"
        level_vi = "NGHIÊM TRỌNG"
        color = "#dc2626"

    return {
        "total_score": total,
        "max_score": 100,
        "level": level,
        "level_vi": level_vi,
        "color": color,
        "breakdown": scores,
    }
