"""
Agent: Inbound (Tiền vào) Reconciler — Cross-check bank-payout emails
against real Wealify VA transactions.

Originally this could only check each email's Ref against the VA account
list — Wealify's per-transaction endpoint (GET /v2/virtual-accounts/transactions)
returns no data on the dev sandbox (verified: HTTP 200, data: null, for all
3 test accounts). GET /v2/transactions/va is a different, working endpoint
that returns real per-transaction VA deposit/withdrawal records, so this
now does the same real matched/pending/mismatch check outbound_reconciler.py
does for card-side (CD-ref) emails.
"""
from __future__ import annotations

import re
from typing import Any

from agents.email_extractor import extract_email_fields


def check_inbound_emails(
    emails: list[dict[str, Any]],
    va_transactions: list[dict[str, Any]] | None = None,
    lang: str = "vi",
) -> dict[str, Any]:
    va_transactions = va_transactions or []
    va_by_id = {t.get("transaction_id", ""): t for t in va_transactions}

    items = []
    for email in emails:
        body = email.get("body", "")
        ref_match = re.search(r"Ref:\s*([A-Z]+-\d+)", body)
        amount_match = re.search(r"received USD\s+([\d.]+)", body, re.IGNORECASE)

        if ref_match is not None or amount_match is not None:
            ref = ref_match.group(1) if ref_match else None
            if ref and not ref.startswith("VA-"):
                continue  # CD-side handled by outbound_reconciler
            email_amount = float(amount_match.group(1)) if amount_match else None
        else:
            # Neither template matched — ask the LLM to read this one
            # instead of silently skipping a real payout notification
            # phrased differently. See agents/email_extractor.py.
            extracted = extract_email_fields(email)
            ref = extracted.get("ref")
            if ref and not str(ref).startswith("VA-"):
                continue  # CD-side handled by outbound_reconciler
            email_amount = extracted.get("amount")
            if ref is None and email_amount is None:
                continue

        full_id = f"WLF15-{ref}" if ref else None
        txn = va_by_id.get(full_id) if full_id else None

        entry: dict[str, Any] = {
            "email_ref": ref,
            "wealify_transaction_id": full_id,
            "email_subject": email.get("subject", ""),
            "email_date": email.get("date", ""),
            "email_from": email.get("from", ""),
            "email_amount": email_amount,
        }

        if txn is None:
            entry["category"] = "not_found_on_wealify"
            entry["label"] = _msg("Chưa đủ dữ liệu", "Insufficient data", lang)
            entry["detail"] = _msg(
                f"Email báo nhận {email_amount} (Ref: {ref}) nhưng KHÔNG tìm thấy giao dịch "
                f"{full_id or ref} trên Wealify.",
                f"Email reports receiving {email_amount} (Ref: {ref}) but no matching "
                f"transaction {full_id or ref} found on Wealify.",
                lang,
            )
        else:
            status = txn.get("va_transaction_status", "")
            wealify_amount = float(txn.get("amount", 0))
            amount_stated = email_amount is not None
            amount_matches = amount_stated and abs(email_amount - wealify_amount) < 0.01
            entry["wealify_amount"] = wealify_amount
            entry["wealify_status"] = status
            entry["currency"] = txn.get("currency_symbol", "")
            entry["amount_matches"] = amount_matches if amount_stated else None

            if status == "SUCCESS" and (amount_matches or not amount_stated):
                entry["category"] = "matched_success"
                entry["label"] = _msg("Định kỳ đã xác định", "Confirmed recurring", lang)
                entry["detail"] = _msg(
                    f"Khớp đúng: email {email_amount} = Wealify {wealify_amount}, trạng thái SUCCESS."
                    if amount_stated
                    else f"Khớp mã tham chiếu với Wealify ({wealify_amount}, SUCCESS).",
                    f"Matched: email {email_amount} = Wealify {wealify_amount}, status SUCCESS."
                    if amount_stated
                    else f"Matched by reference to Wealify ({wealify_amount}, SUCCESS).",
                    lang,
                )
            elif status in ("PROCESSING", "WAITING"):
                entry["category"] = "matched_pending"
                entry["label"] = _msg("Cần bạn tự xác nhận", "Needs your confirmation", lang)
                entry["detail"] = _msg(
                    f"Có ghi nhận trên Wealify nhưng đang ở trạng thái {status} — chưa chốt xong.",
                    f"Recorded on Wealify but still {status} — not settled yet.",
                    lang,
                )
            elif amount_stated and not amount_matches:
                entry["category"] = "amount_mismatch"
                entry["label"] = _msg("Cần bạn tự xác nhận", "Needs your confirmation", lang)
                entry["detail"] = _msg(
                    f"Có ghi nhận trên Wealify ({wealify_amount}) nhưng số tiền lệch với email ({email_amount}).",
                    f"Recorded on Wealify ({wealify_amount}) but amount differs from the email ({email_amount}).",
                    lang,
                )
            else:
                # FAILURE
                entry["category"] = "matched_failed"
                entry["label"] = _msg("Cần bạn tự xác nhận", "Needs your confirmation", lang)
                entry["detail"] = _msg(
                    f"Email báo đã nhận tiền nhưng Wealify ghi nhận trạng thái {status}.",
                    f"Email reports money received but Wealify shows status {status}.",
                    lang,
                )

        items.append(entry)

    by_category: dict[str, int] = {}
    for it in items:
        by_category[it["category"]] = by_category.get(it["category"], 0) + 1

    return {
        "total_checked": len(items),
        "by_category": by_category,
        "items": items,
    }


def _msg(vi: str, en: str, lang: str) -> str:
    return en if lang == "en" else vi
