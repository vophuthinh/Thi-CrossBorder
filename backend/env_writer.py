"""
.env Read/Write Helper — used by the Setup Wizard to persist credentials
the user enters through the UI, so they don't have to hand-edit .env.
Updates existing keys in place, appends new ones, leaves everything else
(comments, ordering, unrelated keys) untouched.
"""
from __future__ import annotations

from pathlib import Path

ENV_PATH = Path(__file__).parent.parent / ".env"


def set_env_values(values: dict[str, str]) -> None:
    """Update (or append) one or more KEY=VALUE lines in .env."""
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    remaining = dict(values)

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        if key in remaining:
            lines[i] = f"{key}={remaining.pop(key)}"

    for key, value in remaining.items():
        lines.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
