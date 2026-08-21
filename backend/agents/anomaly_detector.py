"""
Agent 4: Anomaly Detector — Bắt khoản bất thường & gói "quên huỷ".
Nhận diện gói định kỳ, khoản trùng, khoản lạ, tăng giá âm thầm.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from config import LABEL_CONFIRMED, LABEL_NEEDS_REVIEW, LABEL_INSUFFICIENT, DISPUTE_DEADLINE_DAYS


# Known merchant explanations.
# Kept in sync by hand with finding_engine.py's MERCHANT_DICT — that file
# uses a richer {name, domain} structure for email-domain allowlisting, so
# the two aren't merged into one source, but any merchant recognized in one
# must be added here too (a WALMART/TARGET gap here — and a DG_MEMBERSHIP
# entry present there but missing here — caused the dashboard/chat to call
# merchants "unidentified" that /findings already explained correctly).
MERCHANT_EXPLANATIONS = {
    "AMZN MKTP": "Amazon Marketplace — mua hàng trên Amazon.com",
    "AMZN_MKTP": "Amazon Marketplace — mua hàng trên Amazon.com",
    "SQ *": "Square Point-of-Sale — thanh toán tại cửa hàng dùng Square",
    "SQ_COFFEE": "Cửa hàng cà phê dùng hệ thống thanh toán Square",
    "APPL*ICLOUD": "Apple iCloud+ — dịch vụ lưu trữ đám mây của Apple",
    "APPLE_ICLOUD": "Apple iCloud+ — dịch vụ lưu trữ đám mây của Apple",
    "BLS*BLINKIST": "Blinkist — ứng dụng tóm tắt sách",
    "BLINKIST": "Blinkist — ứng dụng tóm tắt sách",
    "GOOGLE_CLOUD": "Google Cloud Platform — dịch vụ đám mây Google",
    "UBER_EATS": "Uber Eats — đặt đồ ăn qua Uber",
    "UBER_TRIP": "Uber — đi xe qua ứng dụng Uber",
    "CHATGPT": "ChatGPT Plus — đăng ký trả phí OpenAI",
    "CANVA_PRO": "Canva Pro — công cụ thiết kế đồ họa",
    "NETFLIX_COM": "Netflix — dịch vụ xem phim trực tuyến",
    "SPOTIFY_USA": "Spotify Premium — dịch vụ nghe nhạc trực tuyến",
    "ADOBE_CLD": "Adobe Creative Cloud — bộ phần mềm thiết kế Adobe",
    "WALMART": "Walmart — chuỗi bán lẻ Mỹ, mua sắm trực tuyến trên Walmart.com",
    "TARGET": "Target — chuỗi bán lẻ Mỹ, mua sắm trực tuyến trên Target.com",
    "DG MEMBERSHIP": "DoorDash DashPass / DG Membership — gói thành viên giao đồ ăn",
}


def detect_anomalies(
    transactions: list[dict[str, Any]],
    lang: str = "vi",
) -> dict[str, Any]:
    """
    Detect subscriptions, duplicates, unknown merchants, and price hikes.
    Returns structured anomaly report.
    """
    charges = [t for t in transactions if t.get("type") == "charge"]

    subscriptions = _detect_subscriptions(charges)
    price_hikes = _detect_price_hikes(subscriptions)
    unknown_merchants = _detect_unknown_merchants(charges)
    duplicates = _detect_duplicate_charges(charges)

    return {
        "subscriptions": subscriptions,
        "price_hikes": price_hikes,
        "unknown_merchants": unknown_merchants,
        "duplicate_charges": duplicates,
        "total_anomalies": len(price_hikes) + len(unknown_merchants) + len(duplicates),
    }


def _detect_subscriptions(charges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect recurring subscription charges."""
    # Group by merchant code
    by_merchant = defaultdict(list)
    for txn in charges:
        code = txn.get("merchant_code", "")
        if code:
            by_merchant[code].append(txn)

    subscriptions = []
    for merchant_code, txns in by_merchant.items():
        if len(txns) < 2:
            continue  # Need at least 2 occurrences

        # Sort by date
        sorted_txns = sorted(txns, key=lambda x: x["date"])

        # Check if roughly monthly (25-35 day intervals)
        intervals = []
        for i in range(1, len(sorted_txns)):
            d1 = datetime.strptime(sorted_txns[i - 1]["date"], "%Y-%m-%d")
            d2 = datetime.strptime(sorted_txns[i]["date"], "%Y-%m-%d")
            intervals.append((d2 - d1).days)

        avg_interval = sum(intervals) / len(intervals) if intervals else 0

        # Windows matched to finding_engine.py's THRESHOLDS["cadence_windows"]
        # (validated there against the real dataset). The old 20-40 "monthly"
        # window was wide enough that two unrelated purchases 40 days apart
        # (different amounts, same merchant) got called a subscription.
        if 27 <= avg_interval <= 33:
            frequency = "monthly"
        elif 360 <= avg_interval <= 370:
            frequency = "yearly"
        elif 88 <= avg_interval <= 95:
            frequency = "quarterly"
        else:
            continue

        latest = sorted_txns[-1]
        amounts = [abs(t["amount"]) for t in sorted_txns]

        # Predict next charge date
        last_date = datetime.strptime(latest["date"], "%Y-%m-%d")
        next_date = last_date + timedelta(days=int(avg_interval))

        explanation = _explain_merchant(merchant_code, latest.get("description", ""))

        subscriptions.append({
            "merchant_code": merchant_code,
            "description": latest["description"],
            "explanation": explanation,
            "frequency": frequency,
            "current_price": abs(latest["amount"]),
            "previous_prices": amounts[:-1],
            "occurrences": len(sorted_txns),
            "next_charge_date": next_date.strftime("%Y-%m-%d"),
            "label": LABEL_CONFIRMED,
        })

    return subscriptions


def _detect_price_hikes(subscriptions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect silent price increases in subscriptions."""
    hikes = []
    for sub in subscriptions:
        prev_prices = sub.get("previous_prices", [])
        current = sub.get("current_price", 0)

        if prev_prices and current > prev_prices[-1]:
            hikes.append({
                "merchant": sub["description"],
                "explanation": sub.get("explanation", ""),
                "old_price": prev_prices[-1],
                "new_price": current,
                "increase": round(current - prev_prices[-1], 2),
                "increase_pct": round((current - prev_prices[-1]) / prev_prices[-1] * 100, 1),
                "label": LABEL_NEEDS_REVIEW,
            })

    return hikes


def _detect_unknown_merchants(charges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find charges from unrecognized merchants."""
    unknown = []
    for txn in charges:
        code = txn.get("merchant_code", "")
        desc = txn.get("description", "")

        if code.startswith("UNKNOWN") or (code and code not in MERCHANT_EXPLANATIONS):
            explanation = MERCHANT_EXPLANATIONS.get(code, "")
            if not explanation:
                # Try partial match
                for key, exp in MERCHANT_EXPLANATIONS.items():
                    if key in desc:
                        explanation = exp
                        break

            unknown.append({
                "reference": txn["reference"],
                "date": txn["date"],
                "description": desc,
                "amount": txn["amount"],
                "merchant_code": code,
                "explanation": explanation if explanation else "chưa xác định được",
                "dispute_deadline": txn.get("dispute_deadline", ""),
                "label": LABEL_NEEDS_REVIEW if not explanation else LABEL_INSUFFICIENT,
            })

    return unknown


def _detect_duplicate_charges(charges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find same-day same-amount charges that look like duplicates."""
    seen = {}
    duplicates = []

    for txn in charges:
        key = f"{txn['date']}|{txn.get('merchant_code', '')}|{txn['amount']}"
        if key in seen:
            duplicates.append({
                "reference": txn["reference"],
                "duplicate_of": seen[key]["reference"],
                "date": txn["date"],
                "description": txn["description"],
                "amount": txn["amount"],
                "dispute_deadline": txn.get("dispute_deadline", ""),
                "label": LABEL_NEEDS_REVIEW,
            })
        else:
            seen[key] = txn

    return duplicates


def _explain_merchant(code: str, description: str) -> str:
    """Try to explain what a merchant is."""
    if code in MERCHANT_EXPLANATIONS:
        return MERCHANT_EXPLANATIONS[code]
    for key, exp in MERCHANT_EXPLANATIONS.items():
        if key in description:
            return exp
    return "chưa xác định được"
