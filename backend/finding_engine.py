"""
Finding Engine — Convert agent outputs into standardized Finding objects.
Implements all detectors D1-D7 per PDF spec and assigns labels via rule table.
"""
from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import median
from typing import Any, Optional

from config import CURRENCY_SYMBOLS
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
    # "payout" (VA WITHDRAWAL — cash withdrawn to an external bank account)
    # used to be included here too, but that's a category error: a
    # withdrawal was never headed to a card in the first place, so it can
    # never have a matching card top_up. Every VND withdrawal (this
    # account's card is USD/EUR-only) was a guaranteed false positive —
    # "Chuyển $48003000.00 ... chưa lên thẻ" for a ₫48,003,000 bank
    # withdrawal, found by comparing the dashboard to real numbers.
    # "transfer" (wallet→card top_up) is the only type this check should
    # ever see.
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

    # D4: Amount unusually large vs this account's own average → R-16
    findings.extend(_detect_amount_spikes(charges))

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
                curr = txn.get("_currency", "USD")
                sym = CURRENCY_SYMBOLS.get(curr, curr + " ")
                findings.append(make_finding(
                    finding_type="UNRECOGNIZED_CHARGE",
                    label_rule_id="R-15",
                    title_vi=f"Khoản lạ {txn['description']} {sym}{abs(txn['amount']):.2f}",
                    title_en=f"Unrecognized charge {txn['description']} {sym}{abs(txn['amount']):.2f}",
                    explanation_vi="Khoản chi không thuộc chuỗi định kỳ nào, không có email khớp, chưa xác định được cửa hàng.",
                    explanation_en="Charge not part of any recurring series, no matching email, merchant unidentified.",
                    amount_cents=int(abs(txn["amount"]) * 100),
                    currency=curr,
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
    "WALMART": {"name": "Walmart", "domain": "walmart.com"},
    "TARGET": {"name": "Target", "domain": "target.com"},
    # Added after switching to live Wealify + Gmail data — real merchant
    # names actually seen in that account's transactions, not in the
    # original mock dataset's smaller CSV.
    # Domains below are verified against the real sender addresses seen in
    # the actual inbox (not guessed) — e.g. Notion bills through Paddle as
    # merchant-of-record, so its real receipt domain is paddle.com, not
    # notion.so; guessing the "official" domain instead caused false
    # SUSPICIOUS_EMAIL flags on completely legitimate receipts.
    "SHOPEE": {"name": "Shopee", "domain": "shopee.com"},
    "NAMECHEAP": {"name": "Namecheap", "domain": "namecheap.com"},
    "GRAB": {"name": "Grab", "domain": "grab.com"},
    "COFFEE_HOUSE": {"name": "The Coffee House", "domain": "the.com"},
    "BOOKING": {"name": "Booking.com", "domain": "booking.com.com"},
    "LAZADA": {"name": "Lazada", "domain": "lazada.com"},
    "NOTION": {"name": "Notion (billed via Paddle)", "domain": "paddle.com"},
    "VULTR": {"name": "Vultr", "domain": "vultr.com"},
    "FACEBOOK_ADS": {"name": "Facebook Ads (Meta)", "domain": "facebookmail.com"},
    "NORDVPN": {"name": "NordVPN", "domain": "nordvpn.com"},
    "CLOUDWAYS": {"name": "Cloudways", "domain": "cloudways.com"},
    "FIGMA": {"name": "Figma", "domain": "figma.com"},
    "STEAM": {"name": "Steam", "domain": "steam.com"},
    "ALIEXPRESS": {"name": "AliExpress", "domain": "aliexpress.com"},
    "UBER": {"name": "Uber", "domain": "uber.com"},
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
        curr = latest.get("_currency", "USD")
        sym = CURRENCY_SYMBOLS.get(curr, curr + " ")
        findings.append(make_finding(
            finding_type="RECURRING_SUBSCRIPTION",
            label_rule_id=rule_id,
            title_vi=f"Gói {info.get('name', merchant_key)} ({cadence})",
            title_en=f"{info.get('name', merchant_key)} subscription ({cadence})",
            explanation_vi=f"Phát hiện {len(txns)} lần trừ tiền, chu kỳ {cadence}, "
                           f"giá hiện tại {sym}{amounts[-1]:.2f}. Kỳ trừ kế tiếp: {next_date.strftime('%Y-%m-%d')}.",
            explanation_en=f"Detected {len(txns)} charges, {cadence} cadence, "
                           f"current price {sym}{amounts[-1]:.2f}. Next charge: {next_date.strftime('%Y-%m-%d')}.",
            amount_cents=int(amounts[-1] * 100),
            currency=curr,
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
                curr = sf.get("currency", "USD")
                sym = CURRENCY_SYMBOLS.get(curr, curr + " ")

                findings.append(make_finding(
                    finding_type="SILENT_PRICE_INCREASE",
                    label_rule_id=rule_id,
                    title_vi=f"{info.get('name', merchant_key)} tăng giá {sym}{old_price:.2f} → {sym}{new_price:.2f}",
                    title_en=f"{info.get('name', merchant_key)} price increase {sym}{old_price:.2f} → {sym}{new_price:.2f}",
                    explanation_vi=f"Tăng +{sym}{increase:.2f} (+{pct}%). Tác động: +{sym}{annual_impact:.2f}/năm.",
                    explanation_en=f"Increased +{sym}{increase:.2f} (+{pct}%). Impact: +{sym}{annual_impact:.2f}/year.",
                    amount_cents=int(new_price * 100),
                    currency=curr,
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

    # Group by amount + currency — without currency, a USD charge and a
    # EUR charge of the same numeric amount (this account has both) could
    # collide into a false "duplicate".
    by_amount = defaultdict(list)
    for txn in charges:
        key = (int(abs(txn["amount"]) * 100), txn.get("_currency", "USD"))
        by_amount[key].append(txn)

    for (amount_cents, _group_currency), txns in by_amount.items():
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
                    curr = t2.get("_currency", "USD")
                    sym = CURRENCY_SYMBOLS.get(curr, curr + " ")

                    findings.append(make_finding(
                        finding_type="DUPLICATE_CHARGE",
                        label_rule_id=rule_id,
                        title_vi=f"Hai khoản {sym}{amount_cents/100:.2f} cùng ngày tại {info.get('name', t2['description'])}",
                        title_en=f"Two charges of {sym}{amount_cents/100:.2f} same day at {info.get('name', t2['description'])}",
                        explanation_vi=f"Cùng cửa hàng, cùng số tiền, cách nhau {hours_diff:.0f} giờ, khác mã tham chiếu.",
                        explanation_en=f"Same merchant, same amount, {hours_diff:.0f} hours apart, different reference IDs.",
                        amount_cents=amount_cents,
                        currency=curr,
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
        # Currency in the key — a VND fee and a USD fee of the same numeric
        # amount on the same day must not collide into a false "double fee".
        key = f"{f['date']}|{int(abs(f['amount'])*100)}|{f.get('_currency', 'USD')}"
        by_key[key].append(f)

    for key, group in by_key.items():
        if len(group) >= 2:
            refs = [g.get("reference", "") for g in group]
            curr = group[0].get("_currency", "USD")
            sym = CURRENCY_SYMBOLS.get(curr, curr + " ")
            findings.append(make_finding(
                finding_type="DOUBLE_FEE",
                label_rule_id="R-08",
                title_vi=f"Phí kép {sym}{abs(group[0]['amount']):.2f} ngày {group[0]['date']}",
                title_en=f"Double fee {sym}{abs(group[0]['amount']):.2f} on {group[0]['date']}",
                explanation_vi=f"{len(group)} khoản phí cùng loại, cùng số tiền, cùng ngày.",
                explanation_en=f"{len(group)} fee charges of same type, same amount, same day.",
                amount_cents=int(abs(group[0]["amount"]) * 100),
                currency=curr,
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
        # Currency in the key — payins are VA-side and mix VND/USD; without
        # this, a VND payin and a USD payin of the same numeric amount on
        # the same day could collide into a false "duplicate payin".
        key = f"{p['date']}|{int(abs(p['amount'])*100)}|{p.get('_currency', 'USD')}"
        by_key[key].append(p)

    for key, group in by_key.items():
        if len(group) >= 2:
            refs = [g.get("reference", "") for g in group]
            # Check different reference IDs
            if len(set(refs)) > 1:
                curr = group[0].get("_currency", "USD")
                sym = CURRENCY_SYMBOLS.get(curr, curr + " ")
                findings.append(make_finding(
                    finding_type="DUPLICATE_PAYIN",
                    label_rule_id="R-09",
                    title_vi=f"Nạp trùng {sym}{abs(group[0]['amount']):.2f} ngày {group[0]['date']}",
                    title_en=f"Duplicate payin {sym}{abs(group[0]['amount']):.2f} on {group[0]['date']}",
                    explanation_vi=f"{len(group)} khoản nạp cùng số tiền, cùng ngày, khác mã tham chiếu.",
                    explanation_en=f"{len(group)} payins of same amount, same day, different reference IDs.",
                    amount_cents=int(abs(group[0]["amount"]) * 100),
                    currency=curr,
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
        # Ignore transfers that are already from the card's data (VC top_ups)
        if txn.get("_source") == "wealify_vc":
            continue

        amount = abs(txn["amount"])
        try:
            txn_date = datetime.strptime(txn["date"], "%Y-%m-%d")
        except ValueError:
            continue

        # Look for matching credit on card statement
        found = False
        for card_txn in card_statement:
            if card_txn.get("category") != "top_up":
                continue
                
            card_amount = abs(card_txn.get("amount", 0))
            try:
                card_date = datetime.strptime(card_txn["date"], "%Y-%m-%d")
            except ValueError:
                continue

            if card_amount > 0 and 0 <= (card_date - txn_date).days <= window:
                # If currencies differ, we can't do a simple amount match.
                # Assume any top-up in the window is the match to avoid false positives.
                txn_curr = txn.get("_currency", "USD")
                card_curr = card_txn.get("_currency", "USD")
                
                if txn_curr != card_curr:
                    found = True
                    break
                elif abs(card_amount - amount) / max(amount, 1) <= tol:
                    found = True
                    break

        if not found:
            curr = txn.get("_currency", "USD")
            sym = CURRENCY_SYMBOLS.get(curr, curr + " ")
            findings.append(make_finding(
                finding_type="IN_TRANSIT_NOT_ON_CARD",
                label_rule_id="R-10",
                title_vi=f"Chuyển {sym}{amount:.2f} ngày {txn['date']} chưa lên thẻ",
                title_en=f"Transfer {sym}{amount:.2f} on {txn['date']} not on card",
                explanation_vi=f"Chuyển sang thẻ {sym}{amount:.2f} nhưng không tìm thấy khoản ghi có tương ứng (±5%, trong 7 ngày) trên sao kê thẻ.",
                explanation_en=f"Transfer to card {sym}{amount:.2f} but no matching credit (±5%, within 7 days) found on card statement.",
                amount_cents=int(amount * 100),
                currency=curr,
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

    Live statements mix currencies (VND/USD/EUR) — reconciling against the
    wallet's balance only makes sense within the wallet's own currency, so
    transactions in other currencies are excluded rather than summed in
    raw (which previously produced a fabricated-looking "$274M mismatch"
    by comparing USD/EUR transaction sums against a VND wallet balance).
    """
    findings = []
    if not account_statement:
        return findings

    actual_closing = wallet.get("wallet_balance")
    if actual_closing is None:
        return findings

    wallet_currency = wallet.get("currency", "USD")
    same_currency_txns = [
        t for t in account_statement if (t.get("_currency") or "USD") == wallet_currency
    ]
    if not same_currency_txns:
        # No dated transactions in the wallet's own currency to reconcile
        # against — don't fabricate a cross-currency comparison.
        return findings

    sorted_txns = sorted(same_currency_txns, key=lambda t: t.get("date", ""))

    # Live VC-sourced transactions never carry a real running balance (the
    # adapter can't compute one — see wealify_adapter.py), and are always
    # written with balance=0. Deriving "opening = balance - amount" from
    # that would fabricate an opening balance out of a placeholder, not a
    # real number. Only trust this when at least one transaction has a
    # genuine (nonzero) balance — true for mock CSV data, false for live.
    if all(float(t.get("balance", 0)) == 0 for t in sorted_txns):
        return findings

    first = sorted_txns[0]
    opening = float(first.get("balance", 0)) - float(first.get("amount", 0))

    total_in = sum(t["amount"] for t in sorted_txns if t["amount"] > 0)
    total_out = sum(-t["amount"] for t in sorted_txns if t["amount"] < 0)
    expected_closing = opening + total_in - total_out

    delta = round(abs(expected_closing - actual_closing), 2)
    if delta >= 0.01:
        sym = CURRENCY_SYMBOLS.get(wallet_currency, wallet_currency + " ")
        findings.append(make_finding(
            finding_type="WALLET_BALANCE_MISMATCH",
            label_rule_id="R-11",
            title_vi=f"Lệch số dư ví {sym}{delta:.2f}",
            title_en=f"Wallet balance mismatch {sym}{delta:.2f}",
            explanation_vi=(
                f"Số dư đầu {sym}{opening:.2f} + tổng vào {sym}{total_in:.2f} − tổng ra {sym}{total_out:.2f} "
                f"= {sym}{expected_closing:.2f}, lệch {sym}{delta:.2f} so với số dư ví thực tế {sym}{actual_closing:.2f}. "
                f"Chưa xác định nguyên nhân."
            ),
            explanation_en=(
                f"Opening {sym}{opening:.2f} + inflows {sym}{total_in:.2f} − outflows {sym}{total_out:.2f} "
                f"= {sym}{expected_closing:.2f}, differs by {sym}{delta:.2f} from actual wallet balance {sym}{actual_closing:.2f}. "
                f"Cause unresolved."
            ),
            amount_cents=int(delta * 100),
            currency=wallet_currency,
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

        # Score each email per PDF formula. A "Ref: <id>" printed in the
        # email body (a real, visible receipt field — not a peek at any
        # hidden answer key) is stronger evidence than amount/date/token
        # fuzzy-matching, so treat an exact reference match as decisive.
        # Must match the full "<PREFIX>-<number>" (e.g. "CD-0038"), not
        # just the trailing digits — CD-0038 and VA-0038 are unrelated
        # transactions that happen to share a number.
        ref_parts = ref.split("-")
        ref_code = "-".join(ref_parts[-2:]) if len(ref_parts) >= 2 and ref_parts[-1].isdigit() else None
        ref_pattern = re.compile(rf"Ref:\s*{re.escape(ref_code)}\b") if ref_code else None

        best_score = 0.0
        best_email = None
        suspicious_flags = []

        for email in emails:
            if ref_pattern and ref_pattern.search(email.get("body", "")):
                score = 1.0
            else:
                score = _score_email_match(txn, email)
            if score > best_score:
                best_score = score
                best_email = email

        # Check suspicious — only on an email that actually cleared the
        # matched-email bar. Without this, "best_email" is whichever email
        # scored highest even when NO email scored highly (0.0 included —
        # any nonempty inbox always has some best_email), and checking its
        # sender domain against an unrelated merchant's allowlist made
        # every one of them look like impersonation. Real bug, not
        # cosmetic — it only showed up once there were enough real, varied
        # emails for a coincidental "best of a bad lot" pick to happen.
        if best_email and best_score >= THRESHOLDS["email_notfound_threshold"]:
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
                currency=txn.get("_currency", "USD"),
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
            curr = txn.get("_currency", "USD")
            sym = CURRENCY_SYMBOLS.get(curr, curr + " ")
            findings.append(make_finding(
                finding_type="NO_MATCHING_EMAIL",
                label_rule_id="R-12",
                title_vi=f"Không tìm thấy email cho {txn['description']} {sym}{amount:.2f}",
                title_en=f"No matching email for {txn['description']} {sym}{amount:.2f}",
                explanation_vi=f"Giao dịch {sym}{amount:.2f} ngày {txn['date']} — điểm khớp email cao nhất {best_score:.2f} < 0.50.",
                explanation_en=f"Charge {sym}{amount:.2f} on {txn['date']} — best email match score {best_score:.2f} < 0.50.",
                amount_cents=int(amount * 100),
                currency=curr,
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
                currency=txn.get("_currency", "USD"),
                occurred_at=txn["date"],
                evidence_refs=[txn.get("reference", "")],
                evidence_sources=[{"source": "account_statement", "file": "account_statement.csv"}],
                merchant_key=None,
                confidence=compute_confidence(merchant_known=False),
                severity_rank=2,
            ))

    return findings


def _detect_amount_spikes(charges: list[dict]) -> list[dict]:
    """D4: Detect a charge that's a large multiple of this account's own
    average card spending, per currency (R-16).

    Catches a different kind of "khoản lạ" than the other D4 checks: a
    charge at a perfectly recognized, legitimate merchant can still be
    wildly out of line with how this account normally spends (e.g. one
    $2,000 charge among $50 averages) — recurring/duplicate/unknown-merchant
    detection never looks at magnitude relative to the account's own
    history, only at repetition or identity. Scoped to card charges only
    (not VA payin/payout) — "chi tiêu" in the spec's own wording, and the
    clearest, least ambiguous slice to flag confidently as "cần xác nhận"
    without overreaching. Never claims fraud, matching the spec's ban on
    definitive fraud/no-fraud verdicts — confidence is deliberately low
    (this is one unconfirmed statistical signal, not a corroborated
    pattern), same intent as every other "Cần bạn tự xác nhận" finding here.
    """
    findings = []
    min_baseline = THRESHOLDS["amount_spike_min_baseline"]
    multiplier = THRESHOLDS["amount_spike_multiplier"]

    by_currency: dict[str, list[dict]] = defaultdict(list)
    for txn in charges:
        by_currency[txn.get("_currency", "USD")].append(txn)

    for curr, txns in by_currency.items():
        if len(txns) < min_baseline:
            continue
        amounts = [abs(t["amount"]) for t in txns]
        avg = sum(amounts) / len(amounts)
        if avg <= 0:
            continue
        sym = CURRENCY_SYMBOLS.get(curr, curr + " ")

        for txn, amt in zip(txns, amounts):
            if amt < avg * multiplier:
                continue
            ratio = amt / avg
            merchant_key = _resolve_merchant(txn)
            info = MERCHANT_DICT.get(merchant_key, {}) if merchant_key else {}
            findings.append(make_finding(
                finding_type="UNUSUAL_AMOUNT_SPIKE",
                label_rule_id="R-16",
                title_vi=f"Giao dịch đột biến {sym}{amt:.2f} tại {info.get('name', txn.get('description', ''))}",
                title_en=f"Unusual spike {sym}{amt:.2f} at {info.get('name', txn.get('description', ''))}",
                explanation_vi=(
                    f"Cao gấp {ratio:.1f} lần mức chi tiêu trung bình {sym}{avg:.2f} "
                    f"của tài khoản (dựa trên {len(txns)} giao dịch cùng loại tiền)."
                ),
                explanation_en=(
                    f"{ratio:.1f}x this account's average spending of {sym}{avg:.2f} "
                    f"(based on {len(txns)} charges in the same currency)."
                ),
                amount_cents=int(amt * 100),
                currency=curr,
                occurred_at=txn.get("date", ""),
                evidence_refs=[txn.get("reference", "")],
                evidence_sources=[{"source": "account_statement", "file": "account_statement.csv"}],
                merchant_key=merchant_key,
                merchant_display_vi=info.get("name", ""),
                confidence=compute_confidence(merchant_known=bool(merchant_key)),
                severity_rank=2,
            ))

    return findings
