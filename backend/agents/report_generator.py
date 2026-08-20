"""
Agent 5: Report Generator — Báo cáo tài chính tổng hợp.
Tháng/quý/năm + danh sách gói + kỳ trừ kế tiếp + cảnh báo tăng giá.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any


def generate_report(
    statement_analysis: dict[str, Any],
    anomaly_results: dict[str, Any],
    lang: str = "vi",
) -> dict[str, Any]:
    """Generate comprehensive financial report."""

    subscriptions = anomaly_results.get("subscriptions", [])
    price_hikes = anomaly_results.get("price_hikes", [])

    # Subscription summary
    total_monthly_sub = sum(
        s["current_price"] for s in subscriptions if s.get("frequency") == "monthly"
    )
    total_yearly_sub = sum(
        s["current_price"] for s in subscriptions if s.get("frequency") == "yearly"
    )
    projected_annual = total_monthly_sub * 12 + total_yearly_sub

    # Upcoming charges
    upcoming = sorted(
        [
            {
                "service": s["description"],
                "amount": s["current_price"],
                "next_date": s["next_charge_date"],
                "frequency": s["frequency"],
            }
            for s in subscriptions
        ],
        key=lambda x: x["next_date"],
    )

    labels = _labels(lang)

    # --- Monthly / Quarterly / Yearly breakdown ---
    monthly = statement_analysis.get("monthly_breakdown", {})
    quarterly = _aggregate_quarterly(monthly)
    yearly = _aggregate_yearly(monthly)

    return {
        "overview": statement_analysis.get("summary", {}),
        "monthly_breakdown": monthly,
        "quarterly_breakdown": quarterly,
        "yearly_breakdown": yearly,
        "subscriptions": {
            labels["active_subs"]: len(subscriptions),
            labels["monthly_cost"]: round(total_monthly_sub, 2),
            labels["yearly_cost"]: round(total_yearly_sub, 2),
            labels["projected_annual"]: round(projected_annual, 2),
        },
        "upcoming_charges": upcoming,
        "price_hike_alerts": [
            {
                "service": h["merchant"],
                "old": h["old_price"],
                "new": h["new_price"],
                "increase": f"+${h['increase']:.2f} (+{h['increase_pct']}%)",
            }
            for h in price_hikes
        ],
        "top3_largest": statement_analysis.get("top3_largest", []),
    }


def _aggregate_quarterly(monthly: dict[str, dict]) -> dict[str, dict]:
    """Aggregate monthly data into quarterly (Q1-Q4)."""
    quarterly = defaultdict(lambda: {"income": 0, "spending": 0, "fees": 0, "transfers": 0})

    for month_key, data in monthly.items():
        # month_key format: "2026-06"
        try:
            year, month = month_key.split("-")
            month_num = int(month)
            quarter = (month_num - 1) // 3 + 1
            q_key = f"{year}-Q{quarter}"
        except (ValueError, IndexError):
            continue

        quarterly[q_key]["income"] += data.get("income", 0)
        quarterly[q_key]["spending"] += data.get("spending", 0)
        quarterly[q_key]["fees"] += data.get("fees", 0)
        quarterly[q_key]["transfers"] += data.get("transfers", 0)

    # Round all values
    result = {}
    for k, v in sorted(quarterly.items()):
        result[k] = {
            "income": round(v["income"], 2),
            "spending": round(v["spending"], 2),
            "fees": round(v["fees"], 2),
            "transfers": round(v["transfers"], 2),
            "net": round(v["income"] - v["spending"] - v["fees"] - v["transfers"], 2),
        }
    return result


def _aggregate_yearly(monthly: dict[str, dict]) -> dict[str, dict]:
    """Aggregate monthly data into yearly."""
    yearly = defaultdict(lambda: {"income": 0, "spending": 0, "fees": 0, "transfers": 0})

    for month_key, data in monthly.items():
        try:
            year = month_key.split("-")[0]
        except (ValueError, IndexError):
            continue

        yearly[year]["income"] += data.get("income", 0)
        yearly[year]["spending"] += data.get("spending", 0)
        yearly[year]["fees"] += data.get("fees", 0)
        yearly[year]["transfers"] += data.get("transfers", 0)

    result = {}
    for k, v in sorted(yearly.items()):
        result[k] = {
            "income": round(v["income"], 2),
            "spending": round(v["spending"], 2),
            "fees": round(v["fees"], 2),
            "transfers": round(v["transfers"], 2),
            "net": round(v["income"] - v["spending"] - v["fees"] - v["transfers"], 2),
        }
    return result


def _labels(lang: str) -> dict[str, str]:
    if lang == "en":
        return {
            "active_subs": "Active Subscriptions",
            "monthly_cost": "Monthly Subscription Cost",
            "yearly_cost": "Yearly Subscription Cost",
            "projected_annual": "Projected Annual Total",
        }
    return {
        "active_subs": "Gói đang hoạt động",
        "monthly_cost": "Chi phí gói hàng tháng",
        "yearly_cost": "Chi phí gói hàng năm",
        "projected_annual": "Dự báo tổng chi năm",
    }
