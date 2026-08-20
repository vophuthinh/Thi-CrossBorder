"""
Wealify Smart Finance — Configuration
"""
from __future__ import annotations

import os
from pathlib import Path

# --- Mode ---
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# --- LLM ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "byteplus")
BYTEPLUS_API_KEY = os.getenv("BYTEPLUS_API_KEY", "")
BYTEPLUS_ENDPOINT = os.getenv("BYTEPLUS_ENDPOINT", "")
BYTEPLUS_MODEL = os.getenv("BYTEPLUS_MODEL", "doubao-seed-2.0-241228")
BYTEPLUS_BASE_URL = os.getenv(
    "BYTEPLUS_BASE_URL",
    "https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions",
)

# --- Fallback LLM providers ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

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
