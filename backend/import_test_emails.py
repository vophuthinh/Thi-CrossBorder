#!/usr/bin/env python3
"""
One-time script: import the organizer's sample inbox (wlf15_inbox_3users.xlsx)
into the demo Gmail account, so the app can read real test emails via the
Gmail API instead of hand-written mock .txt files.

Usage: python3 import_test_emails.py [sheet_name]
  sheet_name defaults to "wealifytester" (matches WEALIFY_EMAIL in .env).
"""
import sys
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path

import openpyxl

from gmail_client import import_test_emails

XLSX_PATH = Path(__file__).parent.parent / "wlf15_inbox_3users.xlsx"


def _parse_datetime(dt_val) -> str:
    """The xlsx stores 'datetime' as plain text (e.g. '2026-06-06 12:37'),
    not an Excel-native date — openpyxl hands it back as a str, so this
    must parse it explicitly rather than relying on isinstance(datetime)."""
    if isinstance(dt_val, datetime):
        dt = dt_val
    else:
        dt = datetime.strptime(str(dt_val).strip(), "%Y-%m-%d %H:%M")
    return format_datetime(dt)


def load_sheet(sheet_name: str) -> list[dict]:
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0]
    idx = {name: i for i, name in enumerate(header)}

    emails = []
    for row in rows[1:]:
        if not row or row[idx["email_id"]] is None:
            continue
        date_header = _parse_datetime(row[idx["datetime"]])

        emails.append({
            "from": row[idx["from"]] or "",
            "to": row[idx["to"]] or "",
            "subject": row[idx["subject"]] or "",
            "body": row[idx["body"]] or "",
            "date": date_header,
        })
    return emails


def main():
    sheet_name = sys.argv[1] if len(sys.argv) > 1 else "wealifytester"
    print(f"Đọc sheet '{sheet_name}' từ {XLSX_PATH.name}...")
    emails = load_sheet(sheet_name)
    print(f"Tìm thấy {len(emails)} email. Bắt đầu import vào Gmail (lần đầu sẽ mở trình duyệt để xác nhận)...")

    imported = import_test_emails(emails)
    print(f"✅ Đã import {imported}/{len(emails)} email vào hộp thư demo.")


if __name__ == "__main__":
    main()
