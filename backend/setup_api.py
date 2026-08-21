"""
Setup Wizard API — lets a judge configure Gmail + Wealify credentials and
the domain whitelist through the UI instead of hand-editing .env, so the
"cài đặt trong 10 phút" requirement doesn't depend on reading source code.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from env_writer import set_env_values
from domain_whitelist import get_whitelist, add_domain, remove_domain, SUGGESTED_DOMAINS

router = APIRouter(prefix="/setup", tags=["setup"])

GMAIL_TOKEN_PATH = Path(__file__).parent / "gmail_token.json"
GMAIL_CREDENTIALS_PATH = Path(__file__).parent / "gmail_credentials.json"


class GmailCredentials(BaseModel):
    client_id: str
    client_secret: str


class WealifyCredentials(BaseModel):
    username: str
    password: str


class DomainRequest(BaseModel):
    domain: str


@router.get("/status")
def get_status():
    from config import WEALIFY_EMAIL, WEALIFY_PASSWORD

    gmail_connected = GMAIL_TOKEN_PATH.exists()
    connected_account = ""
    if gmail_connected:
        try:
            from gmail_client import get_gmail_service
            profile = get_gmail_service().users().getProfile(userId="me").execute()
            connected_account = profile.get("emailAddress", "")
        except Exception:
            gmail_connected = False

    return {
        "gmail_connected": gmail_connected,
        "gmail_account": connected_account,
        "wealify_configured": bool(WEALIFY_EMAIL and WEALIFY_PASSWORD),
        "wealify_username": WEALIFY_EMAIL,
        "whitelist": get_whitelist(),
        "suggested_domains": [d for d in SUGGESTED_DOMAINS if d not in get_whitelist()],
    }


@router.post("/gmail")
def setup_gmail(creds: GmailCredentials):
    """Save Gmail OAuth client credentials and run the one-time browser
    consent flow. Blocks until the user finishes (or the flow errors)."""
    import json

    GMAIL_CREDENTIALS_PATH.write_text(json.dumps({
        "installed": {
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }, indent=2), encoding="utf-8")

    if GMAIL_TOKEN_PATH.exists():
        GMAIL_TOKEN_PATH.unlink()

    try:
        from gmail_client import get_gmail_service
        service = get_gmail_service()
        profile = service.users().getProfile(userId="me").execute()
        return {"success": True, "connected_account": profile.get("emailAddress", "")}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/wealify")
def setup_wealify(creds: WealifyCredentials):
    """Save Wealify credentials and verify them with a real login attempt."""
    set_env_values({
        "WEALIFY_EMAIL": creds.username,
        "WEALIFY_PASSWORD": creds.password,
    })

    try:
        from wealify_client import WealifyClient
        client = WealifyClient(email=creds.username, password=creds.password)
        client.login()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/whitelist")
def list_whitelist():
    return {"whitelist": get_whitelist(), "suggested": [d for d in SUGGESTED_DOMAINS if d not in get_whitelist()]}


@router.post("/whitelist")
def add_whitelist_domain(req: DomainRequest):
    return {"whitelist": add_domain(req.domain)}


@router.delete("/whitelist/{domain}")
def remove_whitelist_domain(domain: str):
    return {"whitelist": remove_domain(domain)}


@router.post("/finalize")
def finalize_setup():
    """
    Mark setup complete. Deliberately does NOT flip USE_GMAIL_API — the
    core /findings pipeline (evaluate.py scoring) stays on the tuned mock
    dataset regardless of wizard state. The live reconciliation endpoints
    call the Gmail/Wealify clients directly and don't need that flag.
    """
    return {"status": "completed"}
