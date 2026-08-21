"""
Agent 1: Statement Parser — Đọc & phân loại sao kê tài khoản.
Tách rõ: tiền vào, tiền ra, chuyển sang thẻ, phí, chi tiêu.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any


def analyze_statement(transactions: list[dict[str, Any]], lang: str = "vi") -> dict[str, Any]:
    """
    Parse and categorize account statement transactions.

    Live Wealify data mixes multiple currencies in one statement (VND payin,
    USD/EUR card spend) — summing raw amounts across currencies without
    conversion would be meaningless (and converting would require a fake/
    made-up FX rate). So summary/top3/monthly_breakdown are all grouped by
    currency; nothing is added across currencies. Mock data has no
    `_currency` field on transactions, so it's treated as a single "USD"
    group, matching its previous flat-number behavior.
    """
    categories = {
        "payin": [],       # Tiền vào
        "payout": [],      # Tiền ra
        "transfer": [],    # Chuyển sang thẻ
        "fee": [],         # Phí
        "charge": [],      # Chi tiêu (quẹt thẻ)
        "refund": [],      # Hoàn tiền (bù trừ vào chi tiêu)
    }

    # Per-currency running totals: {currency: {total_in, total_out, ...}}
    totals = defaultdict(lambda: {
        "total_in": 0.0, "total_out": 0.0, "total_fees": 0.0,
        "total_charges": 0.0, "total_transfers": 0.0, "txn_count": 0,
    })
    charges_by_currency = defaultdict(list)

    for txn in transactions:
        t = txn.get("type", "unknown")
        amount = txn.get("amount", 0)
        currency = txn.get("_currency") or "USD"
        bucket = totals[currency]
        bucket["txn_count"] += 1

        if t == "payin":
            categories["payin"].append(txn)
            bucket["total_in"] += amount
        elif t in ("payout", "withdrawal"):
            categories["payout"].append(txn)
            bucket["total_out"] += abs(amount)
        elif t == "transfer":
            categories["transfer"].append(txn)
            bucket["total_transfers"] += abs(amount)
        elif t == "fee":
            categories["fee"].append(txn)
            bucket["total_fees"] += abs(amount)
        elif t == "charge":
            categories["charge"].append(txn)
            bucket["total_charges"] += abs(amount)
            charges_by_currency[currency].append(txn)
        elif t == "refund":
            categories["refund"].append(txn)
            bucket["total_in"] += abs(amount)

    # Top 3 largest charges, per currency (comparing amounts across
    # currencies without conversion isn't meaningful).
    top3_by_currency = {}
    for currency, charges in charges_by_currency.items():
        sorted_charges = sorted(charges, key=lambda x: abs(x.get("amount", 0)), reverse=True)
        top3_by_currency[currency] = [
            {"date": t["date"], "description": t["description"], "amount": t["amount"]}
            for t in sorted_charges[:3]
        ]

    # Monthly breakdown, per currency
    monthly = defaultdict(lambda: defaultdict(lambda: {"income": 0, "spending": 0, "fees": 0, "transfers": 0}))
    for txn in transactions:
        currency = txn.get("_currency") or "USD"
        month_key = txn["date"][:7]  # YYYY-MM
        bucket = monthly[currency][month_key]
        amount = txn.get("amount", 0)
        t = txn.get("type", "")
        if t == "payin":
            bucket["income"] += amount
        elif t == "charge":
            bucket["spending"] += abs(amount)
        elif t == "refund":
            bucket["income"] += abs(amount)
        elif t == "fee":
            bucket["fees"] += abs(amount)
        elif t == "transfer":
            bucket["transfers"] += abs(amount)

    labels = _get_labels(lang)

    summary_by_currency = {}
    for currency, b in totals.items():
        summary_by_currency[currency] = {
            labels["total_in"]: round(b["total_in"], 2),
            labels["total_charges"]: round(b["total_charges"], 2),
            labels["total_fees"]: round(b["total_fees"], 2),
            labels["total_transfers"]: round(b["total_transfers"], 2),
            labels["total_out"]: round(b["total_out"], 2),
            labels["net"]: round(
                b["total_in"] - b["total_charges"] - b["total_fees"]
                - b["total_transfers"] - b["total_out"], 2
            ),
            labels["txn_count"]: b["txn_count"],
        }

    return {
        "summary": summary_by_currency,
        "top3_largest": top3_by_currency,
        "monthly_breakdown": {cur: dict(months) for cur, months in monthly.items()},
        "categories": {k: len(v) for k, v in categories.items()},
    }


def _get_labels(lang: str) -> dict[str, str]:
    if lang == "en":
        return {
            "total_in": "Total Income",
            "total_charges": "Total Spending",
            "total_fees": "Total Fees",
            "total_transfers": "Total Transfers to Card",
            "total_out": "Other Withdrawals",
            "net": "Net Balance Change",
            "txn_count": "Transaction Count",
        }
    return {
        "total_in": "Tổng tiền vào",
        "total_charges": "Tổng chi tiêu",
        "total_fees": "Tổng phí",
        "total_transfers": "Tổng chuyển sang thẻ",
        "total_out": "Tổng rút ra khác",
        "net": "Thay đổi số dư ròng",
        "txn_count": "Số giao dịch",
    }
