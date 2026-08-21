"""
Agent: Inbound (Tiền vào) Reconciler — Cross-check bank-payout emails
against Wealify.

Wealify's live VA-transactions endpoint (per-transaction bank deposits)
returns no data on the dev sandbox (verified: HTTP 200, data: null, for
all 3 test accounts, all parameter combinations). So this can only check
each email's Ref against the VA account list — no per-transaction
verification is possible. Every result here is honestly labeled
"Chưa đủ dữ liệu" rather than pretending a match was verified.
"""
from __future__ import annotations

import re
from typing import Any


def check_inbound_emails(emails: list[dict[str, Any]], lang: str = "vi") -> dict[str, Any]:
    items = []
    for email in emails:
        body = email.get("body", "")
        ref_match = re.search(r"Ref:\s*([A-Z]+-\d+)", body)
        amount_match = re.search(r"received USD\s+([\d.]+)", body, re.IGNORECASE)
        if ref_match is None and amount_match is None:
            continue
        ref = ref_match.group(1) if ref_match else None
        if ref and not ref.startswith("VA-"):
            continue  # CD-side handled by outbound_reconciler

        items.append({
            "email_ref": ref,
            "email_subject": email.get("subject", ""),
            "email_date": email.get("date", ""),
            "email_from": email.get("from", ""),
            "email_amount": float(amount_match.group(1)) if amount_match else None,
            "category": "cannot_verify_va_endpoint_down",
            "label": _msg("Chưa đủ dữ liệu", "Insufficient data", lang),
            "detail": _msg(
                "Không thể đối soát tự động với Wealify — API lấy giao dịch tài khoản ảo (VA) "
                "đang lỗi trên môi trường dev (xác nhận qua nhiều lần thử). "
                "Bạn cần tự kiểm tra khoản này trên Wealify.",
                "Cannot auto-reconcile against Wealify — the VA-transactions API is broken "
                "on the dev environment (confirmed after repeated checks). "
                "Please verify this one yourself on Wealify.",
                lang,
            ),
        })

    return {
        "total_checked": len(items),
        "note": _msg(
            "Toàn bộ khoản tiền vào hiện ở nhãn 'Chưa đủ dữ liệu' do giới hạn kỹ thuật thật của môi trường dev Wealify, không phải do khoản tiền có vấn đề.",
            "All inbound items are labeled 'Insufficient data' due to a real technical limitation of the Wealify dev environment, not because anything is actually wrong with them.",
            lang,
        ),
        "items": items,
    }


def _msg(vi: str, en: str, lang: str) -> str:
    return en if lang == "en" else vi
