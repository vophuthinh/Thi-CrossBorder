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
    # monthly is {currency: {month_key: {...}}} — statement mixes VND/USD/EUR,
    # so each currency is aggregated separately, never summed together.
    monthly = statement_analysis.get("monthly_breakdown", {})
    quarterly = {cur: _aggregate_quarterly(months) for cur, months in monthly.items()}
    yearly = {cur: _aggregate_yearly(months) for cur, months in monthly.items()}

    return {
        "overview": statement_analysis.get("summary", {}),
        "monthly_breakdown": monthly,
        "quarterly_breakdown": quarterly,
        "yearly_breakdown": yearly,
        "income_note": income_note(lang),
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


def income_note(lang: str) -> str:
    """
    "Tổng tiền vào" in this report only counts dated card-side transactions
    (refunds). Wealify's virtual-account transaction history API
    (GET /v2/virtual-accounts/transactions) always returns no data, so
    individual, dated VA deposit events can't be reconstructed — showing $0
    income would be misleading, not "no fake data", since real deposits do
    happen. This note makes that gap explicit instead of hiding it.
    """
    if lang == "en":
        return (
            "Note: 'Total Income' here only reflects dated card-side refunds. "
            "Wealify's virtual-account deposit history API is currently "
            "unavailable, so individual deposit transactions can't be listed "
            "or dated — this is NOT the same as zero income. See lifetime "
            "totals per account and the current wallet balance in the "
            "Wealify Accounts tab."
        )
    return (
        "Lưu ý: 'Tổng tiền vào' ở đây chỉ tính các khoản hoàn tiền (refund) có "
        "ngày cụ thể từ thẻ. API lịch sử giao dịch tài khoản ảo (VA) của "
        "Wealify hiện không trả dữ liệu, nên không dựng lại được từng khoản "
        "tiền nạp vào có ngày cụ thể — đây KHÔNG có nghĩa là không có thu "
        "nhập. Xem tổng nhận trọn đời từng tài khoản và số dư ví hiện tại ở "
        "tab Tài khoản Wealify."
    )
