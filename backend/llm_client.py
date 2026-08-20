"""
LLM Client — Unified wrapper for BytePlus Seed 2.0 with fallback to OpenAI / Anthropic.
Supports retry logic, token counting, and provider switching via env var.

Built with BytePlus ModelArk — Seed 2.0
"""
from __future__ import annotations

import json
import time
import httpx
from config import (
    LLM_PROVIDER,
    BYTEPLUS_ENDPOINT,
    BYTEPLUS_API_KEY,
    BYTEPLUS_BASE_URL,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
)

# ─── Provider Configurations ────────────────────────────────

PROVIDERS = {
    "byteplus": {
        "url": BYTEPLUS_BASE_URL,
        "model": BYTEPLUS_ENDPOINT,
        "api_key": BYTEPLUS_API_KEY,
        "headers_fn": lambda key: {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4o",
        "api_key": OPENAI_API_KEY,
        "headers_fn": lambda key: {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    },
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "model": "claude-sonnet-4-20250514",
        "api_key": ANTHROPIC_API_KEY,
        "headers_fn": lambda key: {
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
    },
}


# ─── Token & Cost Tracking ──────────────────────────────────

_usage_log: list[dict] = []


def get_usage_log() -> list[dict]:
    """Return the accumulated usage log for this session."""
    return _usage_log


def get_total_tokens() -> int:
    """Return total tokens used across all calls."""
    return sum(entry.get("total_tokens", 0) for entry in _usage_log)


# ─── Core LLM Call ───────────────────────────────────────────


def call_llm(
    prompt: str,
    system: str = "You are a helpful financial analyst assistant.",
    max_tokens: int = 1500,
    temperature: float = 0.4,
    retries: int = 3,
    provider: str | None = None,
) -> str:
    """
    Call LLM with retry + exponential backoff.
    Powered by BytePlus Seed 2.0.

    Args:
        prompt: User prompt
        system: System message
        max_tokens: Max response tokens
        temperature: Sampling temperature (lower = more deterministic)
        retries: Number of retry attempts
        provider: Override provider (default: use LLM_PROVIDER env var)

    Returns:
        LLM response text
    """
    provider = provider or LLM_PROVIDER
    cfg = PROVIDERS.get(provider)
    if not cfg:
        raise ValueError(f"Unknown LLM provider: {provider}. Use: byteplus, openai, anthropic")

    if not cfg["api_key"]:
        raise ValueError(
            f"API key not set for provider '{provider}'. "
            f"Set the corresponding env var in .env"
        )

    # Build request based on provider
    if provider == "anthropic":
        payload = {
            "model": cfg["model"],
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
    else:
        payload = {
            "model": cfg["model"],
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

    headers = cfg["headers_fn"](cfg["api_key"])
    last_error = None

    for attempt in range(retries):
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(cfg["url"], json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()

            # Extract response text
            if provider == "anthropic":
                text = result["content"][0]["text"]
                tokens = result.get("usage", {})
                total = tokens.get("input_tokens", 0) + tokens.get("output_tokens", 0)
            else:
                text = result["choices"][0]["message"]["content"]
                tokens = result.get("usage", {})
                total = tokens.get("total_tokens", 0)

            # Log usage
            _usage_log.append({
                "provider": provider,
                "model": cfg["model"],
                "total_tokens": total,
                "timestamp": time.time(),
            })

            return text

        except (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout) as e:
            last_error = e
            wait = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            print(f"[LLM] Attempt {attempt + 1}/{retries} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)

    raise RuntimeError(
        f"LLM call failed after {retries} attempts. Last error: {last_error}"
    )


def call_llm_json(
    prompt: str,
    system: str = "You are a helpful financial analyst. Always respond with valid JSON.",
    max_tokens: int = 2000,
    temperature: float = 0.3,
    provider: str | None = None,
) -> dict:
    """
    Call LLM and parse response as JSON.
    Falls back to wrapping raw text if JSON parsing fails.
    """
    raw = call_llm(
        prompt=prompt,
        system=system + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no code fences, no explanation outside JSON.",
        max_tokens=max_tokens,
        temperature=temperature,
        provider=provider,
    )

    # Clean up common issues
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"raw_response": raw, "parse_error": True}
