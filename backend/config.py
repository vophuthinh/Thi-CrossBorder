"""
Wealify Smart Finance — Configuration
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load ../.env (project root) — every os.getenv() below depends on this
# actually having run first, so it must be the first thing this module does.
load_dotenv(Path(__file__).parent.parent / ".env")

# --- Mode ---
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# --- LLM ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "byteplus")
BYTEPLUS_API_KEY = os.getenv("BYTEPLUS_API_KEY", "")
# The model ID sent in API calls (BytePlus Ark "Responses API" takes the plain
# model ID, not the console's Endpoint ID — see llm_client.py).
BYTEPLUS_MODEL = os.getenv("BYTEPLUS_MODEL", "deepseek-v4-flash-260425")
# Console's Endpoint ID, kept for reference/bookkeeping only — not sent in requests.
BYTEPLUS_ENDPOINT = os.getenv("BYTEPLUS_ENDPOINT", "")
BYTEPLUS_BASE_URL = os.getenv(
    "BYTEPLUS_BASE_URL",
    "https://ark.ap-southeast.bytepluses.com/api/v3/responses",
)

# --- Fallback LLM providers ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# --- Wealify API ---
WEALIFY_API_URL = os.getenv("WEALIFY_API_URL", "https://dev-api.wealify.com/api")
WEALIFY_VC_API_URL = os.getenv("WEALIFY_VC_API_URL", "https://dev-api.virtual-card.wealify.com/api")
WEALIFY_EMAIL = os.getenv("WEALIFY_EMAIL", "")
WEALIFY_PASSWORD = os.getenv("WEALIFY_PASSWORD", "")
USE_LIVE_WEALIFY = os.getenv("USE_LIVE_WEALIFY", "false").lower() == "true"

# --- Gmail API (read-only inbox for email reconciliation) ---
USE_GMAIL_API = os.getenv("USE_GMAIL_API", "false").lower() == "true"

# --- Paths ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ACCOUNT_STATEMENT_PATH = DATA_DIR / "account_statement.csv"
CARD_STATEMENT_PATH = DATA_DIR / "card_statement.csv"
WALLET_BALANCE_PATH = DATA_DIR / "wallet_balance.json"
EMAILS_DIR = DATA_DIR / "emails"
AUDIT_LOG_PATH = DATA_DIR / "audit_log.json"

# --- Constants ---
DISPUTE_DEADLINE_DAYS = 60
SUPPORTED_LANGUAGES = ["vi", "en"]
USER_EMAIL = os.getenv("USER_EMAIL", "user@demo-wealify.com")

# --- Periodic monitoring ---
# How often the background job re-fetches data and re-scans for new
# findings (audit_log's dedup keeps it from re-flagging the same item).
SCHEDULED_CHECK_INTERVAL_SECONDS = int(os.getenv("SCHEDULED_CHECK_INTERVAL_SECONDS", "300"))

# --- Outbound email (self-notify only — never third parties) ---
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# --- Labels (3 levels as required by problem statement) ---
LABEL_CONFIRMED = "Định kỳ đã xác định"
LABEL_NEEDS_REVIEW = "Cần bạn tự xác nhận"
LABEL_INSUFFICIENT = "Chưa đủ dữ liệu"

LABEL_CONFIRMED_EN = "Recurring - Confirmed"
LABEL_NEEDS_REVIEW_EN = "Needs your confirmation"
LABEL_INSUFFICIENT_EN = "Insufficient data"

# --- Mandatory Disclaimer ---
DISCLAIMER_VI = (
    "⚠️ Công cụ này chỉ hỗ trợ bạn rà soát tài chính. "
    "Kết quả để tham khảo, không phải kết luận chính thức của Wealify "
    "và không thay cho việc bạn tự kiểm tra. "
    "Nếu thấy giao dịch lạ, hãy liên hệ hỗ trợ ngay — "
    "ở Mỹ thời hạn khiếu nại là 60 ngày kể từ ngày ngân hàng gửi sao kê."
)

DISCLAIMER_EN = (
    "⚠️ This tool only assists you in reviewing your finances. "
    "Results are for reference only, not official Wealify conclusions, "
    "and do not replace your own verification. "
    "If you notice suspicious transactions, contact support immediately — "
    "in the US, the dispute deadline is 60 days from the statement date."
)
