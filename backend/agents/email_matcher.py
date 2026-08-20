"""
Agent 2: Email Matcher — Đối soát giao dịch với email biên lai.
Khớp mỗi giao dịch: "có email khớp / không tìm thấy email / email nghi giả"
"""
from __future__ import annotations

import re
from typing import Any


def match_transactions_to_emails(
    transactions: list[dict[str, Any]],
    emails: list[dict[str, str]],
    lang: str = "vi",
) -> list[dict[str, Any]]:
    """
    Match each charge transaction to emails.
    Returns list of matches with status.
    """
    results = []

    # Only check charge-type transactions
    charge_txns = [t for t in transactions if t.get("type") == "charge"]

    for txn in charge_txns:
        match_result = _find_email_match(txn, emails)
        results.append(match_result)

    return results


def _find_email_match(txn: dict[str, Any], emails: list[dict[str, str]]) -> dict[str, Any]:
    """Find matching email for a transaction."""
    description = txn.get("description", "").lower()
    amount = abs(txn.get("amount", 0))
    txn_date = txn.get("date", "")
    reference = txn.get("reference", "")

    best_match = None
    match_status = "no_email"  # no_email | matched | suspicious_email
    suspicious_reasons = []

    # Extract merchant keywords from description
    merchant_keywords = _extract_merchant_keywords(description)

    for email in emails:
        email_body = email.get("body", "").lower()
        email_subject = email.get("subject", "").lower()
        email_from = email.get("from", "").lower()
        email_text = f"{email_subject} {email_body}"

        # Check if email mentions same amount
        amount_match = _check_amount_in_email(amount, email_text)

        # Check if email matches merchant
        merchant_match = any(kw in email_text for kw in merchant_keywords if len(kw) > 2)

        # Check if reference matches
        ref_match = reference and reference.lower() in email_text

        if amount_match and (merchant_match or ref_match):
            # Found a potential match — now check if email is suspicious
            suspicious = _check_email_suspicious(email)
            if suspicious:
                match_status = "suspicious_email"
                suspicious_reasons = suspicious
                best_match = email
            else:
                match_status = "matched"
                best_match = email
            break
        elif merchant_match and not amount_match:
            # Merchant matches but amount doesn't — could be price change
            if best_match is None:
                match_status = "no_email"
                best_match = email

    result = {
        "reference": reference,
        "date": txn_date,
        "description": txn.get("description", ""),
        "amount": txn.get("amount", 0),
        "match_status": match_status,
    }

    if best_match:
        result["matched_email"] = {
            "filename": best_match.get("filename", ""),
            "subject": best_match.get("subject", ""),
            "from": best_match.get("from", ""),
            "date": best_match.get("date", ""),
        }
    if suspicious_reasons:
        result["suspicious_reasons"] = suspicious_reasons

    return result


def _extract_merchant_keywords(description: str) -> list[str]:
    """Extract searchable keywords from transaction description."""
    # Common merchant name mappings
    known_merchants = {
        "netflix": ["netflix"],
        "spotify": ["spotify"],
        "adobe": ["adobe", "creative cloud"],
        "amazon": ["amazon", "amzn"],
        "google": ["google"],
        "apple": ["apple", "icloud", "appl"],
        "uber": ["uber"],
        "chatgpt": ["chatgpt", "openai"],
        "walmart": ["walmart"],
        "target": ["target"],
        "canva": ["canva"],
        "blinkist": ["blinkist", "bls"],
    }

    keywords = []
    desc_lower = description.lower()
    for merchant, kws in known_merchants.items():
        if any(kw in desc_lower for kw in kws):
            keywords.extend(kws)
            keywords.append(merchant)

    # Also add raw words from description
    words = re.findall(r"[a-z]+", desc_lower)
    keywords.extend([w for w in words if len(w) > 3])

    return list(set(keywords))


def _check_amount_in_email(amount: float, email_text: str) -> bool:
    """Check if the transaction amount appears in email."""
    # Look for dollar amounts in email
    amount_str = f"{amount:.2f}"
    patterns = [
        f"${amount_str}",
        f"$ {amount_str}",
        amount_str,
        f"{amount:.0f}" if amount == int(amount) else "",
    ]
    return any(p and p in email_text for p in patterns)


def _check_email_suspicious(email: dict[str, str]) -> list[str]:
    """
    Check if an email looks suspicious/fake.
    Returns list of reasons or empty list if clean.
    """
    reasons = []
    sender = email.get("from", "")
    subject = email.get("subject", "")
    body = email.get("body", "")

    # Check for misspelled brand names
    misspellings = {
        "blnkist": "blinkist",
        "netfliix": "netflix",
        "spotfy": "spotify",
        "adobee": "adobe",
    }
    for wrong, correct in misspellings.items():
        if wrong in subject.lower() or wrong in body.lower():
            reasons.append(f"Tên thương hiệu bị sai chính tả: '{wrong}' (đúng: '{correct}')")

    # Check for suspicious domains
    if sender:
        domain = sender.split("@")[-1] if "@" in sender else ""
        suspicious_domain_patterns = [
            r"renewal\.net",
            r"billing-.*\.com",
            r"account-.*\.net",
            r"support-.*\.org",
        ]
        for pattern in suspicious_domain_patterns:
            if re.search(pattern, domain):
                reasons.append(f"Tên miền email đáng ngờ: {domain}")

    # Check for suspicious links
    suspicious_link_patterns = [
        r"http://[^\s]*token=",
        r"http://[^\s]*verify",
        r"click here to manage",
    ]
    for pattern in suspicious_link_patterns:
        if re.search(pattern, body.lower()):
            reasons.append("Email chứa đường link đáng ngờ")
            break

    return reasons


def get_match_summary(results: list[dict[str, Any]], lang: str = "vi") -> dict[str, Any]:
    """Summarize email matching results."""
    matched = sum(1 for r in results if r["match_status"] == "matched")
    no_email = sum(1 for r in results if r["match_status"] == "no_email")
    suspicious = sum(1 for r in results if r["match_status"] == "suspicious_email")

    if lang == "en":
        return {
            "total_checked": len(results),
            "matched_with_email": matched,
            "no_email_found": no_email,
            "suspicious_email": suspicious,
        }
    return {
        "tổng_kiểm_tra": len(results),
        "có_email_khớp": matched,
        "không_tìm_thấy_email": no_email,
        "email_nghi_giả": suspicious,
    }
