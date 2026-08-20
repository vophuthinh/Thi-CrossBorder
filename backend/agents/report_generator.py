"""
Agent 5: Report Generator — Báo cáo tài chính tổng hợp.
Tháng/quý/năm + danh sách gói + kỳ trừ kế tiếp + cảnh báo tăng giá.
"""
from __future__ import annotations

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

    return {
        "overview": statement_analysis.get("summary", {}),
        "monthly_breakdown": statement_analysis.get("monthly_breakdown", {}),
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
