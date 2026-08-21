"""
Finding Engine — Convert agent outputs into standardized Finding objects.
Implements all detectors D1-D7 per PDF spec and assigns labels via rule table.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from statistics import median
from typing import Any, Optional

from finding_schema import (
    make_finding,
    compute_confidence,
    THRESHOLDS,
    RULE_TABLE,
)


def generate_all_findings(
    account_statement: list[dict],
    card_statement: list[dict],
    wallet_balance: dict,
    emails: list[dict],
) -> list[dict[str, Any]]:
    """
    Master function: run all detectors and return a list of Finding objects.
    """
    findings = []

    charges = [t for t in account_statement if t.get("type") == "charge"]
    fees = [t for t in account_statement if t.get("type") == "fee"]
    payins = [t for t in account_statement if t.get("type") == "payin"]
    transfers = [t for t in account_statement if t.get("type") == "transfer"]

    # D2: Detect recurring subscriptions → R-01 / R-02
    subs = _detect_recurring(charges)
    findings.extend(subs)

    # D3: Detect silent price increases → R-03 / R-04
    findings.extend(_detect_price_hikes(subs, charges))

    # D4: Detect duplicate charges → R-06 / R-07
    findings.extend(_detect_duplicates(charges))

    # D4: Detect double fees → R-08
    findings.extend(_detect_double_fees(fees))

    # D4: Detect duplicate payins → R-09
    findings.extend(_detect_duplicate_payins(payins))

    # D5: Cross-reconcile 3 sources → R-10, R-11
    findings.extend(_detect_transit(transfers, card_statement))
    findings.extend(_detect_wallet_mismatch(account_statement, wallet_balance))

    # D6: Email matching → R-12, R-13
    findings.extend(_detect_email_issues(charges, emails))

    # D6: Unknown merchants → R-14
    findings.extend(_detect_unknown_merchants(charges))

    # R-15: Unrecognized charges
    recognized_refs = {
        ref
        for f in findings
        for ref in f.get("evidence_refs", [])
    }
    for txn in charges:
        ref = txn.get("reference", "")
        if ref and ref not in recognized_refs:
            merchant_key = _resolve_merchant(txn)
            if merchant_key is None:
                findings.append(make_finding(
                    finding_type="UNRECOGNIZED_CHARGE",
                    label_rule_id="R-15",
                    title_vi=f"Khoản lạ {txn['description']} ${abs(txn['amount']):.2f}",
                    title_en=f"Unrecognized charge {txn['description']} ${abs(txn['amount']):.2f}",
                    explanation_vi="Khoản chi không thuộc chuỗi định kỳ nào, không có email khớp, chưa xác định được cửa hàng.",
                    explanation_en="Charge not part of any recurring series, no matching email, merchant unidentified.",
                    amount_cents=int(abs(txn["amount"]) * 100),
                    occurred_at=txn["date"],
                    evidence_refs=[ref],
                    evidence_sources=[{"source": "account_statement", "file": "account_statement.csv"}],
                    merchant_key=None,
                    confidence=compute_confidence(occurrences=0, merchant_known=False),
                ))

    # Deduplicate by fingerprint
    seen = set()
    unique = []
    for f in findings:
        fp = f.get("fingerprint", "")
        if fp not in seen:
            seen.add(fp)
            unique.append(f)

    return unique


# ─── D2: Recurring Detection ────────────────────────────

MERCHANT_DICT = {
    "NETFLIX_COM": {"name": "Netflix", "domain": "netflix.com"},
    "SPOTIFY_USA": {"name": "Spotify", "domain": "spotify.com"},
    "ADOBE_CLD": {"name": "Adobe Creative Cloud", "domain": "adobe.com"},
    "APPLE_ICLOUD": {"name": "Apple iCloud+", "domain": "apple.com"},
    "APPL*ICLOUD": {"name": "Apple iCloud+", "domain": "apple.com"},
    "CHATGPT": {"name": "ChatGPT Plus (OpenAI)", "domain": "openai.com"},
    "CANVA_PRO": {"name": "Canva Pro", "domain": "canva.com"},
    "AMZN_MKTP": {"name": "Amazon Marketplace", "domain": "amazon.com"},
    "AMZN MKTP": {"name": "Amazon Marketplace", "domain": "amazon.com"},
    "UBER_TRIP": {"name": "Uber (đi lại)", "domain": "uber.com"},
    "UBER_EATS": {"name": "Uber Eats", "domain": "ubereats.com"},
    "GOOGLE_CLOUD": {"name": "Google Cloud", "domain": "google.com"},
    "BLS*BLINKIST": {"name": "Blinkist", "domain": "blinkist.com"},
    "BLINKIST": {"name": "Blinkist", "domain": "blinkist.com"},
    "SQ_COFFEE": {"name": "Square Coffee", "domain": "squareup.com"},
    "DG_MEMBERSHIP": {"name": "DoorDash / DG Membership", "domain": "doordash.com"},
    "PLANET_FIT": {"name": "Planet Fitness", "domain": "planetfitness.com"},
    "GYMSHARK_US": {"name": "Gymshark US", "domain": "gymshark.com"},
}


def _resolve_merchant(txn: dict) -> Optional[str]:
    """Resolve merchant_key from transaction. Returns None if unknown."""
    code = txn.get("merchant_code", "")
    if code in MERCHANT_DICT:
        return code
    # Fuzzy: check if description contains any known key
    desc = txn.get("description", "").upper()
    for key in MERCHANT_DICT:
        if key.replace("_", " ") in desc or key.replace("*", " ") in desc:
            return key
    return None


def _detect_recurring(charges: list[dict]) -> list[dict]:
    """D2: Detect recurring subscriptions using median interval."""
    by_merchant = defaultdict(list)
    for txn in charges:
        key = _resolve_merchant(txn)
        if key:
            by_merchant[key].append(txn)

    findings = []
    cadence_windows = THRESHOLDS["cadence_windows"]
    min_occ = THRESHOLDS["recurring_min_occurrences"]  # 3
    amt_tol = THRESHOLDS["recurring_amount_tolerance"]  # 5%

    for merchant_key, txns in by_merchant.items():
        if len(txns) < 2:
            continue

        sorted_txns = sorted(txns, key=lambda x: x["date"])
        dates = [datetime.strptime(t["date"], "%Y-%m-%d") for t in sorted_txns]
        deltas = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]

        if not deltas:
            continue

        med = median(deltas)
        amounts = [abs(t["amount"]) for t in sorted_txns]
        amt_range = (max(amounts) - min(amounts)) / min(amounts) if min(amounts) > 0 else 0

        # Determine cadence
        cadence = None
        for period, (lo, hi) in cadence_windows.items():
            if lo <= med <= hi:
                cadence = period
                break

        if cadence is None:
            continue

        # R-01 or R-02?
        latest = sorted_txns[-1]
        info = MERCHANT_DICT.get(merchant_key, {})

        if len(txns) >= min_occ and amt_range <= amt_tol:
            rule_id = "R-01"
        else:
            rule_id = "R-02"

        # Predict next charge
        next_date = dates[-1] + timedelta(days=int(med))

        # Store as finding + keep metadata for price hike detection
        findings.append(make_finding(
            finding_type="RECURRING_SUBSCRIPTION",
            label_rule_id=rule_id,
            title_vi=f"Gói {info.get('name', merchant_key)} ({cadence})",
            title_en=f"{info.get('name', merchant_key)} subscription ({cadence})",
            explanation_vi=f"Phát hiện {len(txns)} lần trừ tiền, chu kỳ {cadence}, "
                           f"giá hiện tại ${amounts[-1]:.2f}. Kỳ trừ kế tiếp: {next_date.strftime('%Y-%m-%d')}.",
            explanation_en=f"Detected {len(txns)} charges, {cadence} cadence, "
                           f"current price ${amounts[-1]:.2f}. Next charge: {next_date.strftime('%Y-%m-%d')}.",
            amount_cents=int(amounts[-1] * 100),
            occurred_at=latest["date"],
            evidence_refs=[t.get("reference", "") for t in sorted_txns],
            evidence_sources=[{"source": "account_statement", "file": "account_statement.csv"}],
            merchant_key=merchant_key,
            merchant_display_vi=info.get("name", "chưa xác định được"),
            confidence=compute_confidence(
                occurrences=len(txns),
                amount_match_exact=amt_range == 0,
                amount_match_pct=amt_range,
                merchant_known=True,
            ),
            severity_rank=3,
            # Extra metadata for price hike detection
        ))
        # Store amounts for price hike check
        findings[-1]["_amounts"] = amounts
        findings[-1]["_rule_id"] = rule_id
        findings[-1]["_cadence"] = cadence

    return findings


def _detect_price_hikes(sub_findings: list[dict], charges: list[dict]) -> list[dict]:
    """D3: Detect silent price increases in recurring series."""
    findings = []
    min_delta = THRESHOLDS["price_increase_min_delta"]

    for sf in sub_findings:
        amounts = sf.get("_amounts", [])
        if len(amounts) < 2:
            continue

        for i in range(1, len(amounts)):
            if amounts[i] > amounts[i-1] and (amounts[i] - amounts[i-1]) >= min_delta:
                old_price = amounts[i-1]
                new_price = amounts[i]
                increase = new_price - old_price
                pct = round(increase / old_price * 100, 1) if old_price > 0 else 0

                parent_rule = sf.get("_rule_id", "R-01")
                rule_id = "R-03" if parent_rule == "R-01" else "R-04"
                cadence = sf.get("_cadence", "monthly")

                # Estimate annual impact
                periods_per_year = {"weekly": 52, "monthly": 12, "quarterly": 4, "yearly": 1}
                annual_impact = increase * periods_per_year.get(cadence, 12)

                merchant_key = sf.get("merchant_key")
                info = MERCHANT_DICT.get(merchant_key, {})

                findings.append(make_finding(
                    finding_type="SILENT_PRICE_INCREASE",
                    label_rule_id=rule_id,
                    title_vi=f"{info.get('name', merchant_key)} tăng giá ${old_price:.2f} → ${new_price:.2f}",
                    title_en=f"{info.get('name', merchant_key)} price increase ${old_price:.2f} → ${new_price:.2f}",
                    explanation_vi=f"Tăng +${increase:.2f} (+{pct}%). Tác động: +${annual_impact:.2f}/năm.",
                    explanation_en=f"Increased +${increase:.2f} (+{pct}%). Impact: +${annual_impact:.2f}/year.",
                    amount_cents=int(new_price * 100),
                    occurred_at=sf.get("occurred_at", ""),
                    evidence_refs=sf.get("evidence_refs", []),
                    evidence_sources=[{"source": "account_statement", "file": "account_statement.csv"}],
                    merchant_key=merchant_key,
                    merchant_display_vi=info.get("name", ""),
                    confidence=sf.get("confidence", 0.5),
                    severity_rank=1,
                ))
                break  # Only latest hike per merchant

    return findings


def _detect_duplicates(charges: list[dict]) -> list[dict]:
    """D4: Detect duplicate charges. R-06 (known merchant) or R-07 (unknown)."""
    findings = []
    window_hours = THRESHOLDS["duplicate_time_window_hours"]

    # Group by amount
    by_amount = defaultdict(list)
    for txn in charges:
        by_amount[int(abs(txn["amount"]) * 100)].append(txn)

    for amount_cents, txns in by_amount.items():
        if len(txns) < 2:
            continue
        sorted_txns = sorted(txns, key=lambda x: x["date"])
        for i in range(1, len(sorted_txns)):
            t1 = sorted_txns[i-1]
            t2 = sorted_txns[i]

            # Same merchant?
            m1 = _resolve_merchant(t1)
            m2 = _resolve_merchant(t2)
            same_merchant = m1 and m2 and m1 == m2

            # Different reference?
            r1 = t1.get("reference", "")
            r2 = t2.get("reference", "")
            diff_ref = r1 != r2

            # Within time window?
            try:
                d1 = datetime.strptime(t1["date"], "%Y-%m-%d")
                d2 = datetime.strptime(t2["date"], "%Y-%m-%d")
                hours_diff = abs((d2 - d1).total_seconds()) / 3600
            except ValueError:
                continue

            if diff_ref and hours_diff <= window_hours:
                if (same_merchant or (not m1 and not m2)):
                    rule_id = "R-06" if (m1 or m2) else "R-07"
                    merchant_key = m1 or m2
                    info = MERCHANT_DICT.get(merchant_key, {}) if merchant_key else {}

                    findings.append(make_finding(
                        finding_type="DUPLICATE_CHARGE",
                        label_rule_id=rule_id,
                        title_vi=f"Hai khoản ${amount_cents/100:.2f} cùng ngày tại {info.get('name', t2['description'])}",
                        title_en=f"Two charges of ${amount_cents/100:.2f} same day at {info.get('name', t2['description'])}",
                        explanation_vi=f"Cùng cửa hàng, cùng số tiền, cách nhau {hours_diff:.0f} giờ, khác mã tham chiếu.",
                        explanation_en=f"Same merchant, same amount, {hours_diff:.0f} hours apart, different reference IDs.",
                        amount_cents=amount_cents,
                        occurred_at=t2["date"],
                        evidence_refs=[r1, r2],
                        evidence_sources=[
                            {"source": "account_statement", "file": "account_statement.csv"},
                        ],
                        merchant_key=merchant_key,
                        confidence=compute_confidence(
                            occurrences=2,
                            amount_match_exact=True,
                            merchant_known=bool(merchant_key),
                        ),
                        severity_rank=1,
                    ))

    return findings


def _detect_double_fees(fees: list[dict]) -> list[dict]:
    """D4: Detect double fees (R-08)."""
    findings = []
    by_key = defaultdict(list)
    for f in fees:
        key = f"{f['date']}|{int(abs(f['amount'])*100)}"
        by_key[key].append(f)

    for key, group in by_key.items():
        if len(group) >= 2:
            refs = [g.get("reference", "") for g in group]
            findings.append(make_finding(
                finding_type="DOUBLE_FEE",
                label_rule_id="R-08",
                title_vi=f"Phí kép ${abs(group[0]['amount']):.2f} ngày {group[0]['date']}",
                title_en=f"Double fee ${abs(group[0]['amount']):.2f} on {group[0]['date']}",
                explanation_vi=f"{len(group)} khoản phí cùng loại, cùng số tiền, cùng ngày.",
                explanation_en=f"{len(group)} fee charges of same type, same amount, same day.",
                amount_cents=int(abs(group[0]["amount"]) * 100),
                occurred_at=group[0]["date"],
                evidence_refs=refs,
                evidence_sources=[{"source": "account_statement", "file": "account_statement.csv"}],
                confidence=compute_confidence(occurrences=len(group), amount_match_exact=True),
                severity_rank=1,
            ))

    return findings


def _detect_duplicate_payins(payins: list[dict]) -> list[dict]:
    """D4: Detect duplicate payins (R-09)."""
    findings = []
    by_key = defaultdict(list)
    for p in payins:
        key = f"{p['date']}|{int(abs(p['amount'])*100)}"
        by_key[key].append(p)

    for key, group in by_key.items():
        if len(group) >= 2:
            refs = [g.get("reference", "") for g in group]
            # Check different reference IDs
            if len(set(refs)) > 1:
                findings.append(make_finding(
                    finding_type="DUPLICATE_PAYIN",
                    label_rule_id="R-09",
                    title_vi=f"Nạp trùng ${abs(group[0]['amount']):.2f} ngày {group[0]['date']}",
                    title_en=f"Duplicate payin ${abs(group[0]['amount']):.2f} on {group[0]['date']}",
                    explanation_vi=f"{len(group)} khoản nạp cùng số tiền, cùng ngày, khác mã tham chiếu.",
                    explanation_en=f"{len(group)} payins of same amount, same day, different reference IDs.",
                    amount_cents=int(abs(group[0]["amount"]) * 100),
                    occurred_at=group[0]["date"],
                    evidence_refs=refs,
                    evidence_sources=[{"source": "account_statement", "file": "account_statement.csv"}],
                    confidence=compute_confidence(occurrences=len(group), amount_match_exact=True),
                    severity_rank=2,
                ))

    return findings


def _detect_transit(transfers: list[dict], card_statement: list[dict]) -> list[dict]:
    """D5: Detect transfer_to_card not appearing on card statement (R-10)."""
    findings = []
    window = THRESHOLDS["in_transit_window_days"]
    tol = THRESHOLDS["in_transit_amount_tolerance"]

    for txn in transfers:
        amount = abs(txn["amount"])
        try:
            txn_date = datetime.strptime(txn["date"], "%Y-%m-%d")
        except ValueError:
            continue

        # Look for matching credit on card statement
        found = False
        for card_txn in card_statement:
            card_amount = abs(card_txn.get("amount", 0))
            try:
                card_date = datetime.strptime(card_txn["date"], "%Y-%m-%d")
            except ValueError:
                continue

            if (card_amount > 0 and
                abs(card_amount - amount) / amount <= tol and
                0 <= (card_date - txn_date).days <= window):
                found = True
                break

        if not found:
            findings.append(make_finding(
                finding_type="IN_TRANSIT_NOT_ON_CARD",
                label_rule_id="R-10",
                title_vi=f"Chuyển ${amount:.2f} ngày {txn['date']} chưa lên thẻ",
                title_en=f"Transfer ${amount:.2f} on {txn['date']} not on card",
                explanation_vi=f"Chuyển sang thẻ ${amount:.2f} nhưng không tìm thấy khoản ghi có tương ứng (±5%, trong 7 ngày) trên sao kê thẻ.",
                explanation_en=f"Transfer to card ${amount:.2f} but no matching credit (±5%, within 7 days) found on card statement.",
                amount_cents=int(amount * 100),
                occurred_at=txn["date"],
                evidence_refs=[txn.get("reference", "")],
                evidence_sources=[
                    {"source": "account_statement", "file": "account_statement.csv"},
                    {"source": "card_statement", "file": "card_statement.csv"},
                ],
                confidence=compute_confidence(amount_match_exact=False, amount_match_pct=tol),
                severity_rank=1,
            ))

    return findings


def _detect_wallet_mismatch(account_statement: list[dict], wallet: dict) -> list[dict]:
    """
    D5: Detect wallet balance mismatch (R-11).
    Formula: |(đầu + Σvào − Σra) − cuối| ≥ 1 cent.
    đầu (opening) is derived from the first transaction's running balance;
    cuối (closing) is the wallet's reported current balance.
    """
    findings = []
    if not account_statement:
        return findings

    actual_closing = wallet.get("wallet_balance")
    if actual_closing is None:
        return findings

    sorted_txns = sorted(account_statement, key=lambda t: t.get("date", ""))
    first = sorted_txns[0]
    opening = float(first.get("balance", 0)) - float(first.get("amount", 0))

    total_in = sum(t["amount"] for t in sorted_txns if t["amount"] > 0)
    total_out = sum(-t["amount"] for t in sorted_txns if t["amount"] < 0)
    expected_closing = opening + total_in - total_out

    delta = round(abs(expected_closing - actual_closing), 2)
    if delta >= 0.01:
        findings.append(make_finding(
            finding_type="WALLET_BALANCE_MISMATCH",
            label_rule_id="R-11",
            title_vi=f"Lệch số dư ví ${delta:.2f}",
            title_en=f"Wallet balance mismatch ${delta:.2f}",
            explanation_vi=(
                f"Số dư đầu ${opening:.2f} + tổng vào ${total_in:.2f} − tổng ra ${total_out:.2f} "
                f"= ${expected_closing:.2f}, lệch ${delta:.2f} so với số dư ví thực tế ${actual_closing:.2f}. "
                f"Chưa xác định nguyên nhân."
            ),
            explanation_en=(
                f"Opening ${opening:.2f} + inflows ${total_in:.2f} − outflows ${total_out:.2f} "
                f"= ${expected_closing:.2f}, differs by ${delta:.2f} from actual wallet balance ${actual_closing:.2f}. "
                f"Cause unresolved."
            ),
            amount_cents=int(delta * 100),
            occurred_at=datetime.utcnow().strftime("%Y-%m-%d"),
            evidence_refs=[],
            evidence_sources=[
                {"source": "account_statement", "file": "account_statement.csv"},
                {"source": "wallet_snapshots", "file": "wallet_balance.json"},
            ],
            confidence=0.20,
            severity_rank=2,
        ))

    return findings


def _detect_email_issues(charges: list[dict], emails: list[dict]) -> list[dict]:
    """D6: Detect NO_MATCHING_EMAIL (R-12) and SUSPICIOUS_EMAIL (R-13)."""
    findings = []

    for txn in charges:
        amount = abs(txn.get("amount", 0))
        ref = txn.get("reference", "")
        merchant_key = _resolve_merchant(txn)

        # Score each email per PDF formula
        best_score = 0.0
        best_email = None
        suspicious_flags = []

        for email in emails:
            score = _score_email_match(txn, email)
            if score > best_score:
                best_score = score
                best_email = email

        # Check suspicious
        if best_email:
            suspicious_flags = _check_suspicious_email(best_email, merchant_key)

        # R-13: Suspicious email
        if suspicious_flags:
            findings.append(make_finding(
                finding_type="SUSPICIOUS_EMAIL",
                label_rule_id="R-13",
                title_vi=f"Email nghi giả cho giao dịch {txn['description']}",
                title_en=f"Suspicious email for {txn['description']}",
                explanation_vi=f"Lý do: {'; '.join(suspicious_flags)}.",
                explanation_en=f"Reasons: {'; '.join(suspicious_flags)}.",
                amount_cents=int(amount * 100),
                occurred_at=txn["date"],
                evidence_refs=[ref],
                evidence_sources=[
                    {"source": "account_statement", "file": "account_statement.csv"},
                    {"source": "mailbox", "email_id": best_email.get("filename", "")},
                ],
                merchant_key=merchant_key,
                confidence=compute_confidence(has_email=True, email_suspicious=True, merchant_known=bool(merchant_key)),
                severity_rank=1,
            ))

        # R-12: No matching email
        elif best_score < THRESHOLDS["email_notfound_threshold"]:
            findings.append(make_finding(
                finding_type="NO_MATCHING_EMAIL",
                label_rule_id="R-12",
                title_vi=f"Không tìm thấy email cho {txn['description']} ${amount:.2f}",
                title_en=f"No matching email for {txn['description']} ${amount:.2f}",
                explanation_vi=f"Giao dịch ${amount:.2f} ngày {txn['date']} — điểm khớp email cao nhất {best_score:.2f} < 0.50.",
                explanation_en=f"Charge ${amount:.2f} on {txn['date']} — best email match score {best_score:.2f} < 0.50.",
                amount_cents=int(amount * 100),
                occurred_at=txn["date"],
                evidence_refs=[ref],
                evidence_sources=[{"source": "account_statement", "file": "account_statement.csv"}],
                merchant_key=merchant_key,
                confidence=compute_confidence(has_email=False, merchant_known=bool(merchant_key)),
                severity_rank=3,
            ))

    return findings


def _score_email_match(txn: dict, email: dict) -> float:
    """Score email match per PDF D6 formula."""
    amount = abs(txn.get("amount", 0))
    body = (email.get("body", "") + " " + email.get("subject", "")).lower()

    # Amount match (0.5 weight)
    amount_str = f"{amount:.2f}"
    amount_exact = amount_str in body
    amount_score = 1.0 if amount_exact else 0.0

    # Date match (0.2 weight)
    try:
        txn_date = datetime.strptime(txn["date"], "%Y-%m-%d")
        email_date = datetime.strptime(email.get("date", "")[:10], "%Y-%m-%d")
        day_diff = abs((txn_date - email_date).days)
        date_score = 1.0 if day_diff <= THRESHOLDS["email_date_window_days"] else 0.0
    except (ValueError, TypeError):
        date_score = 0.0

    # Merchant token overlap (0.3 weight)
    desc_tokens = set(txn.get("description", "").lower().split())
    email_tokens = set(body.split())
    overlap = len(desc_tokens & email_tokens)
    token_score = min(overlap / max(len(desc_tokens), 1), 1.0)

    return 0.5 * amount_score + 0.2 * date_score + 0.3 * token_score


def _check_suspicious_email(email: dict, merchant_key: Optional[str]) -> list[str]:
    """Check if email is suspicious per PDF D6 step 4."""
    flags = []
    sender = email.get("from", "")
    domain = sender.split("@")[-1].lower() if "@" in sender else ""
    reply_to = email.get("reply_to", "")
    reply_domain = reply_to.split("@")[-1].lower() if "@" in reply_to else ""

    # Allowlist check
    if merchant_key and merchant_key in MERCHANT_DICT:
        expected_domain = MERCHANT_DICT[merchant_key].get("domain", "")
        if expected_domain and expected_domain not in domain:
            flags.append(f"Domain {domain} không thuộc allowlist của {merchant_key}")

    # Lookalike domain (Levenshtein ≤ 2)
    if merchant_key and merchant_key in MERCHANT_DICT:
        expected = MERCHANT_DICT[merchant_key].get("domain", "")
        if expected and domain and domain != expected:
            dist = _levenshtein(domain, expected)
            if dist <= THRESHOLDS["lookalike_domain_distance"]:
                flags.append(f"Domain lookalike: {domain} ≈ {expected} (distance={dist})")

    # Reply-to mismatch
    if reply_domain and domain and reply_domain != domain:
        flags.append(f"Reply-to ({reply_domain}) khác domain gửi ({domain})")

    return flags


def _levenshtein(s1: str, s2: str) -> int:
    """Simple Levenshtein distance."""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


def _detect_unknown_merchants(charges: list[dict]) -> list[dict]:
    """D6: Detect unknown merchants (R-14)."""
    findings = []
    for txn in charges:
        merchant_key = _resolve_merchant(txn)
        if merchant_key is None:
            findings.append(make_finding(
                finding_type="UNKNOWN_MERCHANT",
                label_rule_id="R-14",
                title_vi=f"Cửa hàng không xác định: {txn['description']}",
                title_en=f"Unknown merchant: {txn['description']}",
                explanation_vi="Chưa xác định được.",
                explanation_en="Unidentified.",
                amount_cents=int(abs(txn["amount"]) * 100),
                occurred_at=txn["date"],
                evidence_refs=[txn.get("reference", "")],
                evidence_sources=[{"source": "account_statement", "file": "account_statement.csv"}],
                merchant_key=None,
                confidence=compute_confidence(merchant_known=False),
                severity_rank=2,
            ))

    return findings
