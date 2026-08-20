"""
Agent 1: Statement Parser — Đọc & phân loại sao kê tài khoản.
Tách rõ: tiền vào, tiền ra, chuyển sang thẻ, phí, chi tiêu.
"""
from __future__ import annotations

from typing import Any


def analyze_statement(transactions: list[dict[str, Any]], lang: str = "vi") -> dict[str, Any]:
    """
    Parse and categorize account statement transactions.
    Returns categorized breakdown + summary.
    """
    categories = {
        "payin": [],       # Tiền vào
        "payout": [],      # Tiền ra
        "transfer": [],    # Chuyển sang thẻ
        "fee": [],         # Phí
        "charge": [],      # Chi tiêu (quẹt thẻ)
    }

    total_in = 0.0
    total_out = 0.0
    total_fees = 0.0
    total_charges = 0.0
    total_transfers = 0.0

    for txn in transactions:
        t = txn.get("type", "unknown")
        amount = txn.get("amount", 0)

        if t == "payin":
            categories["payin"].append(txn)
            total_in += amount
        elif t == "payout":
            categories["payout"].append(txn)
            total_out += abs(amount)
        elif t == "transfer":
            categories["transfer"].append(txn)
            total_transfers += abs(amount)
        elif t == "fee":
            categories["fee"].append(txn)
            total_fees += abs(amount)
        elif t == "charge":
            categories["charge"].append(txn)
            total_charges += abs(amount)

    # Top 3 largest charges
    sorted_charges = sorted(categories["charge"], key=lambda x: abs(x.get("amount", 0)), reverse=True)
    top3 = sorted_charges[:3]

    # Monthly breakdown
    monthly = {}
    for txn in transactions:
        month_key = txn["date"][:7]  # YYYY-MM
        if month_key not in monthly:
            monthly[month_key] = {"income": 0, "spending": 0, "fees": 0, "transfers": 0}
        amount = txn.get("amount", 0)
        t = txn.get("type", "")
        if t == "payin":
            monthly[month_key]["income"] += amount
        elif t == "charge":
            monthly[month_key]["spending"] += abs(amount)
        elif t == "fee":
            monthly[month_key]["fees"] += abs(amount)
        elif t == "transfer":
            monthly[month_key]["transfers"] += abs(amount)

    labels = _get_labels(lang)

    return {
        "summary": {
            labels["total_in"]: round(total_in, 2),
            labels["total_charges"]: round(total_charges, 2),
            labels["total_fees"]: round(total_fees, 2),
            labels["total_transfers"]: round(total_transfers, 2),
            labels["net"]: round(total_in - total_charges - total_fees - total_transfers, 2),
            labels["txn_count"]: len(transactions),
        },
        "top3_largest": [
            {
                "date": t["date"],
                "description": t["description"],
                "amount": t["amount"],
            }
            for t in top3
        ],
        "monthly_breakdown": monthly,
        "categories": {k: len(v) for k, v in categories.items()},
    }


def _get_labels(lang: str) -> dict[str, str]:
    if lang == "en":
        return {
            "total_in": "Total Income",
            "total_charges": "Total Spending",
            "total_fees": "Total Fees",
            "total_transfers": "Total Transfers to Card",
            "net": "Net Balance Change",
            "txn_count": "Transaction Count",
        }
    return {
        "total_in": "Tổng tiền vào",
        "total_charges": "Tổng chi tiêu",
        "total_fees": "Tổng phí",
        "total_transfers": "Tổng chuyển sang thẻ",
        "net": "Thay đổi số dư ròng",
        "txn_count": "Số giao dịch",
    }
