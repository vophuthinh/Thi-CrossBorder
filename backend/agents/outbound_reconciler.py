"""
Agent: Outbound (Tiền ra) Reconciler — Match card-payment receipt emails
against real Wealify VC (Virtual Card) transactions.

Extracts the "Ref: XXX" line printed in the email body (a genuine visible
receipt field, not a hidden ground-truth lookup) and checks it against the
live VC transaction list by exact ID, cross-checked by amount.
"""
from __future__ import annotations

import re
from typing import Any

from finding_engine import _levenshtein
from agents.email_extractor import extract_email_fields


def check_suspicious_domains(
    emails: list[dict[str, Any]],
    whitelist: list[str],
    lang: str = "vi",
) -> list[dict[str, Any]]:
    """
    Scan every email's sender domain against the user's whitelist — flags
    lookalike domains (small edit distance from a whitelisted one) as
    "Cần bạn tự xác nhận". Domains that are neither whitelisted nor a
    lookalike are left alone (not enough basis to call them suspicious —
    most are just unrelated real senders like promo emails).
    """
    flags = []
    whitelist_set = set(whitelist)
    # Compare by brand-name token, not the full domain string — "wealify.com"
    # vs "wea1ify-support.com" differ by 9 chars overall (mostly the added
    # "-support"), but the actual brand token "wea1ify" is 1 edit away from
    # "wealify". Whole-string distance would miss that entirely.
    brand_names = {known.split(".")[0] for known in whitelist_set}

    for email in emails:
        sender = email.get("from", "")
        domain = sender.split("@")[-1].strip().lower().rstrip(">")
        if not domain or domain in whitelist_set:
            continue

        tokens = re.split(r"[.\-]", domain)

        best_match, best_dist = None, 99
        for token in tokens:
            for brand in brand_names:
                if token == brand:
                    continue  # exact brand token present — not a lookalike
                dist = _levenshtein(token, brand)
                if dist < best_dist:
                    best_match, best_dist = brand, dist

        if best_match and 0 < best_dist <= 2:
            flags.append({
                "email_from": sender,
                "email_subject": email.get("subject", ""),
                "email_date": email.get("date", ""),
                "lookalike_of": best_match,
                "edit_distance": best_dist,
                "label": _msg("Cần bạn tự xác nhận", "Needs your confirmation", lang),
                "detail": _msg(
                    f"Domain người gửi '{domain}' rất giống '{best_match}' (đã tin cậy) nhưng không khớp — có thể là giả mạo.",
                    f"Sender domain '{domain}' closely resembles the trusted '{best_match}' but doesn't match exactly — possible impersonation.",
                    lang,
                ),
            })
    return flags


def match_outbound_emails(
    emails: list[dict[str, Any]],
    vc_transactions: list[dict[str, Any]],
    lang: str = "vi",
) -> dict[str, Any]:
    """
    Luồng Tiền ra: thanh toán thẻ / gói định kỳ.
    Only handles CD-prefixed refs (card-side) — VA-prefixed refs (bank payout)
    can't be verified because the live VA-transactions endpoint is broken;
    those are left to the caller to report separately.
    """
    vc_by_id = {t.get("transaction_id", ""): t for t in vc_transactions}
    results = []

    for email in emails:
        body = email.get("body", "")
        ref_match = re.search(r"Ref:\s*([A-Z]+-\d+)", body)
        amount_match = re.search(r"Amount\s+([\d.]+)", body)

        if ref_match and ref_match.group(1).startswith("CD-"):
            ref = ref_match.group(1)
            email_amount = float(amount_match.group(1)) if amount_match else None
        else:
            # Regex template didn't match — ask the LLM to read this one
            # instead of silently skipping a real receipt phrased
            # differently. See agents/email_extractor.py.
            extracted = extract_email_fields(email)
            if not extracted.get("ref") or not str(extracted["ref"]).startswith("CD-"):
                continue
            ref = extracted["ref"]
            email_amount = extracted.get("amount")

        full_id = f"WLF15-{ref}"

        txn = vc_by_id.get(full_id)
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
            entry["label"] = _msg(
                "Chưa đủ dữ liệu",
                "Insufficient data", lang)
            entry["detail"] = _msg(
                f"Email báo thanh toán ${email_amount} (Ref: {ref}) nhưng KHÔNG tìm thấy giao dịch {full_id} trên Wealify.",
                f"Email reports a ${email_amount} payment (Ref: {ref}) but no matching transaction {full_id} found on Wealify.",
                lang)
        else:
            status = txn.get("transaction_vc_status", "")
            wealify_amount = float(txn.get("amount", 0))
            # None = email simply didn't state an amount (some templates just
            # say "Thanks") — that's not a mismatch, just nothing to cross-check.
            amount_stated = email_amount is not None
            amount_matches = amount_stated and abs(email_amount - wealify_amount) < 0.01
            entry["wealify_amount"] = wealify_amount
            entry["wealify_status"] = status
            entry["card_name"] = txn.get("_card_name", "")
            entry["amount_matches"] = amount_matches if amount_stated else None

            if status == "SUCCESS" and (amount_matches or not amount_stated):
                entry["category"] = "matched_success"
                entry["label"] = _msg("Định kỳ đã xác định", "Confirmed recurring", lang)
                if amount_stated:
                    entry["detail"] = _msg(
                        f"Khớp đúng: email ${email_amount} = Wealify ${wealify_amount}, trạng thái SUCCESS.",
                        f"Matched: email ${email_amount} = Wealify ${wealify_amount}, status SUCCESS.", lang)
                else:
                    entry["detail"] = _msg(
                        f"Khớp mã tham chiếu với Wealify (${wealify_amount}, SUCCESS) — email không nêu rõ số tiền để đối chiếu thêm.",
                        f"Matched by reference to Wealify (${wealify_amount}, SUCCESS) — email didn't state an amount to cross-check.", lang)
            elif status in ("PENDING", "PROCESSING"):
                entry["category"] = "matched_pending"
                entry["label"] = _msg("Cần bạn tự xác nhận", "Needs your confirmation", lang)
                entry["detail"] = _msg(
                    f"Có ghi nhận trên Wealify nhưng đang ở trạng thái {status} — chưa chốt xong.",
                    f"Recorded on Wealify but still {status} — not settled yet.", lang)
            elif amount_stated and not amount_matches:
                entry["category"] = "amount_mismatch"
                entry["label"] = _msg("Cần bạn tự xác nhận", "Needs your confirmation", lang)
                entry["detail"] = _msg(
                    f"Có ghi nhận trên Wealify (${wealify_amount}) nhưng số tiền lệch với email (${email_amount}).",
                    f"Recorded on Wealify (${wealify_amount}) but amount differs from the email (${email_amount}).", lang)
            else:
                # FAILURE / CANCEL
                entry["category"] = "matched_failed_or_cancelled"
                entry["label"] = _msg("Cần bạn tự xác nhận", "Needs your confirmation", lang)
                entry["detail"] = _msg(
                    f"Email báo đã thanh toán nhưng Wealify ghi nhận trạng thái {status}.",
                    f"Email reports a payment but Wealify shows status {status}.", lang)

        results.append(entry)

    by_category: dict[str, int] = {}
    for r in results:
        by_category[r["category"]] = by_category.get(r["category"], 0) + 1

    return {
        "total_checked": len(results),
        "by_category": by_category,
        "items": results,
    }


def _msg(vi: str, en: str, lang: str) -> str:
    return en if lang == "en" else vi
