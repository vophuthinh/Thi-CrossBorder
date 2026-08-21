#!/usr/bin/env python3
"""Regression tests for configurable reminder thresholds."""
import unittest
from unittest.mock import patch

import reminder_checker


class ReminderCheckerTests(unittest.TestCase):
    def test_rejects_non_positive_thresholds(self):
        with patch.object(reminder_checker, "CONFIG_PATH") as config_path:
            config_path.parent.mkdir = unittest.mock.Mock()
            with self.assertRaises(ValueError):
                reminder_checker.save_reminder_config(
                    {"inbound_email_hours": 0, "processing_status_hours": 48}
                )

    def test_flags_processing_transaction_past_threshold(self):
        transactions = [
            {
                "date": "2020-01-01",
                "merchant": "Example",
                "amount": -10,
                "status": "processing",
                "reference": "TX-1",
            }
        ]
        flagged = reminder_checker.check_stale_processing_transactions(transactions, 1)
        self.assertEqual([item["reference"] for item in flagged], ["TX-1"])

    def test_flags_unverified_inbound_email_past_threshold(self):
        emails = [
            {
                "subject": "Payment received",
                "date": "Wed, 01 Jan 2020 10:00:00 +0000",
                "body": "Ref: VA-123\nWe received USD 100.00",
            }
        ]
        flagged = reminder_checker.check_stale_unverified_inbound_emails(emails, 1)
        self.assertEqual([item["email_ref"] for item in flagged], ["VA-123"])


if __name__ == "__main__":
    unittest.main()