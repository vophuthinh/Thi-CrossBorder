#!/usr/bin/env python3
"""Regression tests for pre-generated report cache behavior."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report_cache


class ReportCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.report_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_generates_all_twelve_months_and_year(self):
        transactions = [{"date": "2026-08-20", "_record_at": "2026-08-20T10:00:00Z"}]
        with patch.object(report_cache, "REPORT_DIR", self.report_dir), patch.object(
            report_cache, "_build_report", return_value={"ok": True}
        ), patch.object(report_cache, "datetime", _FixedDateTime):
            report_cache.generate_and_cache_reports(transactions, {})

        self.assertEqual(
            {path.stem for path in self.report_dir.glob("*.json")},
            {f"2026-{month:02d}" for month in range(1, 13)} | {"2026"},
        )

    def test_refreshes_when_record_timestamp_is_newer(self):
        current_month = self.report_dir / "2026-08.json"
        current_month.write_text(
            json.dumps(
                {
                    "generated_at": "2026-08-22T09:00:00+00:00",
                    "newest_record_at_generation": "2026-08-20T10:00:00Z",
                    "report": {},
                }
            )
        )

        transactions = [{"date": "2026-08-20", "_record_at": "2026-08-22T10:00:00Z"}]
        with patch.object(report_cache, "REPORT_DIR", self.report_dir), patch.object(
            report_cache, "_build_report", return_value={"ok": True}
        ), patch.object(report_cache, "datetime", _FixedDateTime):
            refreshed = report_cache.refresh_current_month_if_stale(transactions, {})

        self.assertTrue(refreshed)
        saved = json.loads(current_month.read_text())
        self.assertEqual(saved["newest_record_at_generation"], "2026-08-22T10:00:00Z")


class _FixedDateTime:
    @classmethod
    def now(cls, tz=None):
        from datetime import datetime, timezone

        return datetime(2026, 8, 22, 12, 0, tzinfo=timezone.utc)


if __name__ == "__main__":
    unittest.main()