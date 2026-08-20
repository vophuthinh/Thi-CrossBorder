"""
Audit Log — Track every flag/alert, prevent duplicate alerts, export to file.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from config import AUDIT_LOG_PATH


class AuditLog:
    """Persistent audit log for flagged transactions."""

    def __init__(self, path: Path | None = None):
        self.path = path or AUDIT_LOG_PATH
        self.entries: list[dict[str, Any]] = []
        self._load()

    def _load(self):
        """Load existing log from file."""
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.entries = []

    def _save(self):
        """Persist log to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

    def log_flag(
        self,
        transaction_ref: str,
        reason: str,
        confidence: str,
        label: str,
        source: str,
        details: str = "",
    ) -> bool:
        """
        Log a flag. Returns False if already flagged (duplicate prevention).
        """
        if self.is_already_flagged(transaction_ref, reason):
            return False

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "transaction_ref": transaction_ref,
            "reason": reason,
            "confidence": confidence,
            "label": label,
            "source": source,
            "details": details,
        }
        self.entries.append(entry)
        self._save()
        return True

    def is_already_flagged(self, transaction_ref: str, reason: str = "") -> bool:
        """Check if a transaction has already been flagged (for duplicate prevention)."""
        for entry in self.entries:
            if entry["transaction_ref"] == transaction_ref:
                if not reason or entry.get("reason") == reason:
                    return True
        return False

    def get_all_flags(self) -> list[dict[str, Any]]:
        """Return all flag entries."""
        return self.entries.copy()

    def export_flags(self, filepath: str | None = None) -> str:
        """Export flags to JSON and JSONL files. Returns the filepath."""
        export_path = filepath or str(self.path.parent / "audit_log_export.json")
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

        # Also export as JSONL (required by checklist)
        jsonl_path = export_path.replace(".json", ".jsonl")
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for entry in self.entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return export_path

    def clear(self):
        """Clear all entries (for cleanup after competition)."""
        self.entries = []
        self._save()

    def get_summary(self) -> dict[str, Any]:
        """Get summary statistics of flagged items."""
        labels = {}
        for entry in self.entries:
            lbl = entry.get("label", "unknown")
            labels[lbl] = labels.get(lbl, 0) + 1

        return {
            "total_flags": len(self.entries),
            "by_label": labels,
            "latest_flag": self.entries[-1] if self.entries else None,
        }


# Global instance
audit_log = AuditLog()
