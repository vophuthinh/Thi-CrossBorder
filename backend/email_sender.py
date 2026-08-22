"""
Outbound email — sends self-notify reports via the Gmail API (the same
read-only-plus-send-scoped credentials already used to reconcile the
inbox), falling back to SMTP only if Gmail API isn't set up.

This module only ever sends to the address the caller passes in (chat.py
always passes USER_EMAIL, the user's own address — see email_drafter.py).
It never sends to third parties (merchants, banks, support). If neither
Gmail API nor SMTP is configured, sending fails loudly instead of silently
pretending to succeed.
"""
from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from pathlib import Path

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, USE_GMAIL_API

_CREDENTIALS_PATH = Path(__file__).parent / "gmail_credentials.json"


class EmailSendError(Exception):
    pass


def _gmail_available() -> bool:
    return USE_GMAIL_API and _CREDENTIALS_PATH.exists()


def is_configured() -> bool:
    return _gmail_available() or bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def send_email(to: str, subject: str, body: str) -> None:
    """Send a plain-text email. Raises EmailSendError on failure."""
    if _gmail_available():
        from gmail_client import send_email as gmail_send

        try:
            gmail_send(to, subject, body)
            return
        except Exception as e:
            raise EmailSendError(str(e)) from e

    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD):
        raise EmailSendError(
            "Chưa cấu hình cách gửi email — cần USE_GMAIL_API=true (dùng chung "
            "Gmail API đã đọc mail) hoặc SMTP_HOST/SMTP_USER/SMTP_PASSWORD trong .env"
        )

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [to], msg.as_string())
    except Exception as e:
        raise EmailSendError(str(e)) from e
