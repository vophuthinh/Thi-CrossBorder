#!/usr/bin/env python3
"""
test_chat_numbers.py — Regression suite for numeric accuracy in /chat.

Motivated by a real bug: "tháng 2 có bao nhiêu giao dịch" fell through to
the free-form LLM fallback (no month-filtered data in its context) and
answered with two different wrong numbers on two tries (617, then 594),
instead of the real 59. This script computes ground truth directly from
the same functions the app uses (report_cache, detect_anomalies,
wallet_balance), asks the running server the equivalent question over
/chat, and checks whether the expected number actually appears in the
response text — catching exactly this class of "chatbot invents a number"
bug instead of relying on eyeballing individual replies.

Usage: python3 test_chat_numbers.py [--base-url http://localhost:8000]
Requires the backend server to already be running.
"""
from __future__ import annotations

import argparse
import re
import sys
from typing import Any

import requests

import report_cache
from config import CURRENCY_SYMBOLS
from data_loader import get_all_data
from agents.anomaly_detector import detect_anomalies


def extract_numbers(text: str) -> list[float]:
    """Pull every plausible number out of free-text — handles thousands
    separators (1,234.56) and bare decimals (1234.56) so a value shown
    either way is still recognized."""
    raw = re.findall(r"[\d]{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?", text)
    out = []
    for r in raw:
        try:
            out.append(float(r.replace(",", "")))
        except ValueError:
            continue
    return out


def number_in_text(expected: float, text: str, rel_tol: float = 0.02, abs_tol: float = 0.5) -> bool:
    """True if `expected` (or something within tolerance) appears anywhere
    in the response — tolerant of rounding since the chatbot may format
    with fewer decimals than the ground truth."""
    found = extract_numbers(text)
    for f in found:
        if abs(f - expected) <= max(abs_tol, abs(expected) * rel_tol):
            return True
    return False


def build_cases() -> list[dict[str, Any]]:
    """Ground truth computed directly — never via HTTP — so a bug in the
    server's own computation can't hide by matching itself."""
    data = get_all_data()
    anomalies = detect_anomalies(data["account_statement"], "vi")
    wallet = data["wallet_balance"]

    cases: list[dict[str, Any]] = []

    # Month-specific transaction counts — the exact bug this suite exists
    # to catch. One case per currency per month actually present.
    for month in range(1, 13):
        key = f"2026-{month:02d}"
        cached = report_cache.get_cached_report(key)
        if cached is None:
            continue
        overview = cached["report"].get("overview", {})
        for currency, group in overview.items():
            count = group.get("Số giao dịch")
            if count is None:
                continue
            cases.append({
                "name": f"month_txn_count_{key}_{currency}",
                "message": f"Tháng {month} có bao nhiêu giao dịch?",
                "expected": float(count),
                "note": f"{key} [{currency}] Số giao dịch = {count}",
            })

    # Subscriptions / duplicates — deterministic-intent sanity baseline.
    cases.append({
        "name": "subscription_count",
        "message": "Tôi có bao nhiêu gói đăng ký đang hoạt động?",
        "expected": float(len(anomalies["subscriptions"])),
        "note": f"len(subscriptions) = {len(anomalies['subscriptions'])}",
    })
    cases.append({
        "name": "duplicate_count",
        "message": "Có bao nhiêu khoản bị trùng lặp?",
        "expected": float(len(anomalies["duplicate_charges"])),
        "note": f"len(duplicate_charges) = {len(anomalies['duplicate_charges'])}",
    })

    # Real wallet balance — same check used earlier this session against
    # a live Wealify screenshot; kept here so a future regression is caught
    # automatically instead of needing another manual screenshot compare.
    cases.append({
        "name": "wallet_balance",
        "message": "Số dư ví hiện tại là bao nhiêu?",
        "expected": float(wallet["wallet_balance"]),
        "note": f"wallet_balance = {wallet['wallet_balance']}",
    })

    return cases


def run(base_url: str) -> int:
    cases = build_cases()
    print(f"Running {len(cases)} numeric accuracy checks against {base_url}/chat\n")

    passed = 0
    failed = []
    for case in cases:
        try:
            res = requests.post(f"{base_url}/chat", json={"message": case["message"]}, timeout=60)
            res.raise_for_status()
            response_text = res.json().get("response", "")
        except Exception as e:
            failed.append((case, f"request failed: {e}"))
            continue

        if number_in_text(case["expected"], response_text):
            passed += 1
        else:
            failed.append((case, response_text))

    print(f"PASS: {passed}/{len(cases)}\n")
    if failed:
        print(f"FAILED ({len(failed)}):")
        for case, response_text in failed:
            print(f"  - [{case['name']}] Q: {case['message']!r}")
            print(f"    expected ~{case['expected']} ({case['note']})")
            print(f"    got: {response_text[:200]!r}")
            print()

    return 0 if not failed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()
    sys.exit(run(args.base_url))
