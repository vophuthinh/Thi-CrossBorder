"""
Agent: Email Classifier — LLM-based promotional vs transactional filter.

Rule-based matching in email_matcher.py only checks amount/merchant-keyword/
reference — a promotional email ("Shopee giảm giá 50% hôm nay!") can share
the same merchant keyword as a real receipt, and occasionally an amount
that coincidentally matches a transaction, causing a false "matched" or
polluting which email gets picked as the best candidate. This classifies
each email once (batched, one LLM call) as transactional or promotional so
email_matcher.py can exclude promotional ones from the candidate pool
before its existing amount/keyword/ref logic runs — the classification is
a pre-filter, not a replacement for the deterministic matching itself.

Fails safe: if the LLM is unavailable or the call errors, every email is
left unclassified (is_promotional=False) — the matcher behaves exactly as
it did before this existed, never silently drops a real receipt because
classification failed.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger("email_classifier")

# Classification is re-run on every data load (startup, /reset, each
# periodic scheduled check) but real inbox content barely changes between
# those — cache by "filename" (the Gmail message id, stable across
# reloads) so only genuinely new emails pay the LLM call.
_CACHE_PATH = Path(__file__).parent.parent / "data" / "email_classification_cache.json"


def _load_cache() -> dict[str, bool]:
    if _CACHE_PATH.exists():
        try:
            return json.loads(_CACHE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(cache: dict[str, bool]) -> None:
    try:
        _CACHE_PATH.write_text(json.dumps(cache))
    except OSError:
        pass

_SYSTEM = (
    "You classify emails as either a real transaction/receipt/subscription/bank "
    "notification, or promotional marketing content, based only on subject/sender/"
    "snippet. A merchant name appearing is not enough — 'Shopee giảm giá 50%' is "
    "promotional even though it says 'Shopee'; 'Your Shopee order #123 receipt' is "
    "transactional. When genuinely unsure, classify as transactional (a missed "
    "promotional email is harmless; a receipt wrongly hidden is not)."
)


_BATCH_SIZE = 30  # one call for all ~150 emails timed out; smaller batches finish reliably


def classify_emails(emails: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return the same email dicts with an added is_promotional bool field."""
    if not emails:
        return emails

    from config import BYTEPLUS_API_KEY

    # Cache is read regardless of whether a key is currently configured —
    # if BYTEPLUS_API_KEY goes missing later (env reset, key rotation),
    # previously-classified emails must keep their real label instead of
    # silently reverting to "unclassified". Only genuinely new emails need
    # the LLM call, and only run it when a key is actually available.
    cache = _load_cache()
    to_classify = [e for e in emails if e.get("filename", "") not in cache]

    if to_classify and BYTEPLUS_API_KEY:
        newly_classified: list[dict[str, str]] = []
        for start in range(0, len(to_classify), _BATCH_SIZE):
            batch = to_classify[start : start + _BATCH_SIZE]
            newly_classified.extend(_classify_batch(batch))
        for e in newly_classified:
            key = e.get("filename", "")
            if key:
                cache[key] = e["is_promotional"]
        _save_cache(cache)

    return [{**e, "is_promotional": cache.get(e.get("filename", ""), False)} for e in emails]


def _classify_batch(emails: list[dict[str, str]]) -> list[dict[str, str]]:
    try:
        from llm_client import call_llm_json

        lines = []
        for i, e in enumerate(emails):
            snippet = (e.get("body", "") or "")[:150].replace("\n", " ")
            lines.append(
                f'{i}: subject="{e.get("subject", "")}" from="{e.get("from", "")}" snippet="{snippet}"'
            )
        prompt = (
            "Classify each email below. Respond with ONLY a JSON object mapping "
            'each index (as a string) to "transactional" or "promotional".\n\n'
            + "\n".join(lines)
        )
        result = call_llm_json(prompt, system=_SYSTEM, max_tokens=2000, temperature=0.1, timeout=45.0)

        if result.get("parse_error"):
            logger.warning("[email_classifier] LLM response wasn't valid JSON — leaving this batch unfiltered")
            return [{**e, "is_promotional": False} for e in emails]

        classified = []
        for i, e in enumerate(emails):
            label = result.get(str(i)) or result.get(i)
            classified.append({**e, "is_promotional": label == "promotional"})
        return classified

    except Exception as ex:
        logger.warning("[email_classifier] batch classification failed (%s) — leaving this batch unfiltered", ex)
        return [{**e, "is_promotional": False} for e in emails]
