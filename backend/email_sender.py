"""
Outbound email — SMTP sender for self-notify reports.

This module only ever sends to the address the caller passes in (chat.py
always passes USER_EMAIL, the user's own address — see email_drafter.py).
It never sends to third parties (merchants, banks, support). If SMTP isn't
configured, sending fails loudly instead of silently pretending to succeed.
"""
from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD


class EmailSendError(Exception):
    pass


def is_configured() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def send_email(to: str, subject: str, body: str) -> None:
    """Send a plain-text email via SMTP (STARTTLS). Raises EmailSendError on failure."""
    if not is_configured():
        raise EmailSendError(
            "SMTP chưa được cấu hình (set SMTP_HOST/SMTP_USER/SMTP_PASSWORD trong .env)"
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
