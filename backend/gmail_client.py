"""
Gmail API Client — reads the demo inbox for email reconciliation and sends
self-notify reports.

Scoped to exactly the two things WLF-01 permits: gmail.readonly (read the
inbox to reconcile) and gmail.send (send — never insert/modify/delete —
and only ever to the user's own address, see email_sender.py). No
gmail.insert or gmail.modify: the mailbox was already seeded once via
import_test_emails.py, which needed insert at the time but isn't part of
this app's runtime. Per WLF-01's "chìa khoá chỉ đọc, chặn từ khâu cấp
quyền" for money/account actions and "chỉ GỬI CHO CHÍNH NGƯỜI DÙNG" for
email — enforced by the OAuth grant itself, not just by the app never
calling other write endpoints.
"""
from __future__ import annotations

import base64
import threading
from concurrent.futures import ThreadPoolExecutor
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).parent
CREDENTIALS_PATH = BASE_DIR / "gmail_credentials.json"
TOKEN_PATH = BASE_DIR / "gmail_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def _get_credentials() -> Credentials:
    """
    Load (or obtain via one-time browser consent) OAuth credentials.
    Safe to call from multiple threads — googleapiclient's Http transport
    isn't thread-safe, but the Credentials object just holds/refreshes a
    token, which is.
    """
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())

    return creds


def get_gmail_service():
    """
    Get an authorized Gmail API service. Opens a browser for one-time
    consent the first time (needs a human at the keyboard); reuses the
    saved token afterward.
    """
    return build("gmail", "v1", credentials=_get_credentials())


_thread_local = threading.local()


def _thread_service():
    """Per-thread service instance — googleapiclient's Http transport isn't
    thread-safe, so parallel fetches each need their own service object."""
    if not hasattr(_thread_local, "service"):
        _thread_local.service = build("gmail", "v1", credentials=_get_credentials())
    return _thread_local.service


def fetch_emails(max_results: int = 300) -> list[dict[str, str]]:
    """
    Read messages from the inbox, in the same shape data_loader.load_emails()
    returns (from/to/subject/date/body), so downstream matching code doesn't
    care whether emails came from local .txt files or a real Gmail inbox.
    """
    service = get_gmail_service()
    result = service.users().messages().list(
        userId="me", maxResults=max_results, labelIds=["INBOX"]
    ).execute()
    message_ids = [m["id"] for m in result.get("messages", [])]

    def _fetch_one(mid: str) -> dict[str, str]:
        msg = _thread_service().users().messages().get(userId="me", id=mid, format="full").execute()
        headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
        body = _extract_body(msg["payload"])
        email = {
            "filename": mid,
            "from": headers.get("from", ""),
            "to": headers.get("to", ""),
            "subject": headers.get("subject", ""),
            "date": headers.get("date", ""),
            "body": body,
        }
        _prefer_body_embedded_headers(email)
        return email

    # Each message needs its own HTTP round-trip (Gmail API has no bulk-get);
    # fetching sequentially took ~40s for ~150 messages. Threads help since
    # this is I/O-bound; each thread gets its own service via a fresh
    # http build to keep googleapiclient's HTTP objects thread-safe.
    with ThreadPoolExecutor(max_workers=10) as pool:
        emails = list(pool.map(_fetch_one, message_ids))
    return emails


def _prefer_body_embedded_headers(email: dict[str, str]) -> None:
    """
    Gmail's own envelope Date header isn't reliable for backdated inserts on
    a personal (non-Workspace) account — it can silently fall back to
    receipt time regardless of internalDateSource. The seed dataset's body
    text starts with its own "From:/To:/Date:/Subject:" lines (same
    convention data_loader._parse_email_file uses for local .txt files), so
    prefer those when present — they're plain text Gmail never touches.
    Mutates email in place.
    """
    lines = email["body"].split("\n")
    parsed: dict[str, str] = {}
    body_start = 0
    for i, line in enumerate(lines):
        lower = line.lower()
        if lower.startswith("from:"):
            parsed["from"] = line[5:].strip()
        elif lower.startswith("to:"):
            parsed["to"] = line[3:].strip()
        elif lower.startswith("subject:"):
            parsed["subject"] = line[8:].strip()
        elif lower.startswith("date:"):
            parsed["date"] = line[5:].strip()
        elif line.strip() == "" and body_start == 0 and parsed:
            body_start = i + 1
            break

    if "date" in parsed:
        email["from"] = parsed.get("from", email["from"])
        email["to"] = parsed.get("to", email["to"])
        email["subject"] = parsed.get("subject", email["subject"])
        email["date"] = parsed["date"]
        if body_start > 0:
            email["body"] = "\n".join(lines[body_start:]).strip()


def _extract_body(payload: dict) -> str:
    """Recursively find the text/plain part of a Gmail message payload."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        text = _extract_body(part)
        if text:
            return text
    data = payload.get("body", {}).get("data")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    return ""


def send_email(to: str, subject: str, body: str) -> None:
    """
    Send a plain-text email via the Gmail API (messages().send — never
    insert/modify). Caller is responsible for only ever passing the user's
    own address; see email_sender.py, which chat.py's self-notify flow
    goes through exclusively.
    """
    service = get_gmail_service()
    msg = MIMEText(body, "plain", "utf-8")
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


def import_test_emails(emails: list[dict[str, Any]]) -> int:
    """
    One-time seed: insert emails directly into the mailbox (they show up
    as normal received mail) without actually sending/spoofing SMTP.
    Each dict needs: from, to, subject, body, and optionally date.
    Returns the count imported.
    """
    service = get_gmail_service()
    count = 0
    for e in emails:
        msg = MIMEText(e["body"])
        msg["from"] = e["from"]
        msg["to"] = e["to"]
        msg["subject"] = e["subject"]
        if e.get("date"):
            msg["date"] = e["date"]
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().insert(
            userId="me",
            body={"raw": raw, "labelIds": ["INBOX"]},
            internalDateSource="dateHeader",
        ).execute()
        count += 1
    return count
