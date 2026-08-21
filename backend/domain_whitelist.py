"""
Domain Whitelist — user-managed list of email sender domains trusted to
send transaction receipts. Backs both the Setup Wizard's whitelist step
and the suspicious-email check in outbound_reconciler.py.
"""
from __future__ import annotations

import json
from pathlib import Path

WHITELIST_PATH = Path(__file__).parent / "data" / "domain_whitelist.json"

# Shown as one-click suggestions in the wizard — real domains seen in this
# account's own verified data (VA payout platforms + confirmed VC receipts).
SUGGESTED_DOMAINS = [
    "wealify.com",
    "payoneer.com", "paypal.com", "amazon.com", "etsy.com", "pingpongx.com",
    "netflix.com", "spotify.com", "adobe.com", "google.com", "openai.com",
    "figma.com", "canva.com", "namecheap.com", "nordvpn.com", "cloudways.com",
]


def get_whitelist() -> list[str]:
    if not WHITELIST_PATH.exists():
        return []
    return json.loads(WHITELIST_PATH.read_text(encoding="utf-8"))


def add_domain(domain: str) -> list[str]:
    domains = get_whitelist()
    domain = domain.strip().lower()
    if domain and domain not in domains:
        domains.append(domain)
        _save(domains)
    return domains


def remove_domain(domain: str) -> list[str]:
    domains = [d for d in get_whitelist() if d != domain.strip().lower()]
    _save(domains)
    return domains


def _save(domains: list[str]) -> None:
    WHITELIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    WHITELIST_PATH.write_text(json.dumps(domains, indent=2), encoding="utf-8")
