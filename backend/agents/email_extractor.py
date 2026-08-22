"""
Agent: Email Field Extractor — LLM fallback for emails that don't match the
known "Ref: CD-XXXX" / "Ref: VA-XXXX" / "received USD X.XX" regex templates.

outbound_reconciler.py and inbound_reconciler.py only recognize those exact
printed formats — a real receipt/payout email phrased any other way was
silently skipped entirely, never even considered for matching. This asks
the LLM to pull the same two fields (reference, amount) out of whatever
format the email actually uses, so it can still be checked against
Wealify instead of being invisible.

Cached by Gmail message id ("filename") so the same email is never sent to
the LLM twice — the first real hit for a given template effectively teaches
the cache going forward, which is the same "learn once, reuse after" idea
as email_classifier.py's cache.

Fails safe: no API key, or the LLM finds nothing that looks like a real
reference/amount, both return the same {"ref": None, "amount": None} shape
the caller already treats as "no template matched" — this never invents a
reference or amount that isn't actually in the email.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("email_extractor")

_CACHE_PATH = Path(__file__).parent.parent / "data" / "email_extraction_cache.json"

_EMPTY: dict[str, Any] = {"ref": None, "amount": None, "currency": None}

_SYSTEM = (
    "You extract a Wealify transaction reference and amount from a bank/card "
    "notification email, when present. The reference always looks like "
    "'CD-0123' (card payment) or 'VA-0123' (bank/wallet deposit or withdrawal) "
    "— it may appear without the word 'Ref' or in a different position than "
    "usual. Respond with ONLY a JSON object: "
    '{"ref": "CD-0123" or "VA-0123" or null, "amount": number or null, '
    '"currency": "USD" or "VND" or "EUR" or null}. '
    "If this is a promotional email, or you don't see anything that looks "
    "like a real transaction reference, return all null — never guess or "
    "invent a reference/amount that isn't actually written in the email."
)


def _load_cache() -> dict[str, dict]:
    if _CACHE_PATH.exists():
        try:
            return json.loads(_CACHE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(cache: dict[str, dict]) -> None:
    try:
        _CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2))
    except OSError:
        pass


def extract_email_fields(email: dict[str, Any]) -> dict[str, Any]:
    """Return {"ref": str|None, "amount": float|None, "currency": str|None}
    for one email, using the LLM only when neither field is already cached."""
    key = email.get("filename", "")
    cache = _load_cache()
    if key and key in cache:
        return cache[key]

    from config import BYTEPLUS_API_KEY

    if not BYTEPLUS_API_KEY:
        return dict(_EMPTY)

    try:
        from llm_client import call_llm_json

        body = (email.get("body", "") or "")[:1200]
        prompt = f'subject="{email.get("subject", "")}"\nbody="""{body}"""'
        # DeepSeek V4 Flash is a reasoning model — its internal "thinking"
        # tokens count against max_tokens before the actual JSON answer, so
        # a small budget (tried 150 first) cuts the response off mid-thought
        # before any output_text exists at all (verified: every call failed
        # with incomplete_details.reason="length"). Same headroom llm_client.py's
        # other callers already use for this reason.
        result = call_llm_json(prompt, system=_SYSTEM, max_tokens=1000, temperature=0.0, timeout=25.0)

        if result.get("parse_error"):
            extracted = dict(_EMPTY)
        else:
            ref = result.get("ref")
            amount = result.get("amount")
            extracted = {
                "ref": ref if isinstance(ref, str) and ref.strip() else None,
                "amount": float(amount) if isinstance(amount, (int, float)) else None,
                "currency": result.get("currency") if isinstance(result.get("currency"), str) else None,
            }
    except Exception as ex:
        logger.warning("[email_extractor] extraction failed (%s) — treating as no template match", ex)
        extracted = dict(_EMPTY)

    if key:
        cache[key] = extracted
        _save_cache(cache)
    return extracted
