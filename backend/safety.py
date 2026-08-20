"""
Safety Guardrails — Trap question detection, response validation, disclaimers.
Ensures the AI assistant is READ-ONLY and never makes definitive safety claims.
"""
from __future__ import annotations

import re
from config import DISCLAIMER_VI, DISCLAIMER_EN

# --- Trap question patterns ---
TRAP_PATTERNS = {
    "cancel_service": {
        "patterns": [
            r"(tự |giúp |hộ )?(huỷ|hủy|cancel|unsubscribe|ngừng|dừng).*(gói|subscription|dịch vụ|service|netflix|spotify|adobe)",
            r"(huỷ|hủy|cancel).*(mấy gói|all|tất cả)",
            r"tự.*(huỷ|hủy|cancel)",
        ],
        "response_vi": (
            "🚫 Mình không thể tự huỷ gói thay bạn — đây là nguyên tắc an toàn để bảo vệ tài khoản của bạn.\n\n"
            "Tuy nhiên, mình có thể:\n\n"
            "- Liệt kê các gói đăng ký hiện tại\n\n"
            "- Hướng dẫn bạn cách tự huỷ từng gói\n\n"
            "- Soạn bản nháp email để bạn tự gửi\n\n"
            "Bạn muốn mình làm việc nào?"
        ),
        "response_en": (
            "🚫 I cannot cancel subscriptions on your behalf — this is a safety measure to protect your account.\n\n"
            "However, I can:\n\n"
            "- List your current subscriptions\n\n"
            "- Guide you on how to cancel each one\n\n"
            "- Draft an email for you to send yourself\n\n"
            "Which would you like?"
        ),
    },
    "send_email_third_party": {
        "patterns": [
            r"(gửi|send).*(email|mail|thư).*(cho|to|tới|đến).*(netflix|spotify|adobe|ngân hàng|bank|cửa hàng|store|merchant|bên thứ ba|third party)",
            r"(gửi|send).*(khiếu nại|complaint|dispute|chargeback)",
            r"(email|mail).*(khiếu nại|complaint).*(cho|to|giúp|help)",
        ],
        "response_vi": (
            "🚫 Mình chỉ được gửi email tới chính bạn, không được gửi cho bên thứ ba (cửa hàng, ngân hàng...).\n\n"
            "Tuy nhiên, mình có thể soạn bản nháp email khiếu nại để bạn tự gửi.\n\n"
            "Bạn muốn mình soạn nháp cho khoản giao dịch nào?"
        ),
        "response_en": (
            "🚫 I can only send emails to you directly, not to third parties (merchants, banks, etc.).\n\n"
            "However, I can draft a complaint email for you to send yourself.\n\n"
            "Which transaction would you like me to draft an email for?"
        ),
    },
    "safety_reassurance": {
        "patterns": [
            r"(tài khoản|account).*(an toàn|safe|secure|ổn|ok)",
            r"(có|is).*(an toàn|safe|secure|bị hack|compromised)",
            r"(mình|tôi|i).*(bị|been).*(hack|lừa|scam|fraud)",
        ],
        "response_vi": (
            "🚫 Mình không thể kết luận tài khoản của bạn an toàn hay không — điều này cần được Wealify hoặc ngân hàng xác nhận chính thức.\n\n"
            "Thay vào đó, mình có thể giúp bạn:\n\n"
            "- Rà soát các khoản giao dịch bất thường\n\n"
            "- Đối chiếu sao kê với email biên lai\n\n"
            "- Chỉ ra các khoản cần bạn tự xác nhận\n\n"
            "Bạn muốn mình rà soát không?"
        ),
        "response_en": (
            "🚫 I cannot conclude whether your account is safe or not — this requires official confirmation from Wealify or your bank.\n\n"
            "Instead, I can help you:\n\n"
            "- Review suspicious transactions\n\n"
            "- Cross-check statements with email receipts\n\n"
            "- Flag items that need your confirmation\n\n"
            "Would you like me to review?"
        ),
    },
    "transfer_money": {
        "patterns": [
            r"(chuyển|transfer|gửi|send).*(tiền|money|funds|dollars|\$)",
            r"(hoàn|refund|trả).*(tiền|money)",
            r"(khoá|khóa|lock|block|mở|open|unlock).*(thẻ|card|tài khoản|account)",
        ],
        "response_vi": (
            "🚫 Mình không có quyền thao tác tiền hay thẻ — không chuyển tiền, không hoàn tiền, không khoá/mở thẻ.\n\n"
            "Đây là nguyên tắc bảo mật tuyệt đối.\n\n"
            "Nếu bạn cần thực hiện các thao tác này, hãy liên hệ trực tiếp Wealify Support."
        ),
        "response_en": (
            "🚫 I do not have permission to handle money or cards — no transfers, refunds, or card lock/unlock.\n\n"
            "This is a strict security principle.\n\n"
            "If you need these actions, please contact Wealify Support directly."
        ),
    },
}

# --- Banned phrases (must never appear in responses) ---
BANNED_PHRASES_VI = [
    "tài khoản của bạn an toàn",
    "không có gì bất thường",
    "hoàn toàn an toàn",
    "yên tâm",
    "không sao đâu",
    "chắc chắn là gian lận",
    "đây là gian lận",
    "đây không phải gian lận",
    "giao dịch đang bị ngân hàng giữ",
    "đang bị điều tra",
]

BANNED_PHRASES_EN = [
    "your account is safe",
    "nothing unusual",
    "completely safe",
    "don't worry",
    "definitely fraud",
    "this is fraud",
    "this is not fraud",
    "being held by the bank",
    "under investigation",
]


def detect_trap_question(message: str) -> str | None:
    """
    Detect if the message is a 'trap' question that should be refused.
    Returns trap type string or None if not a trap.
    """
    lower = message.lower().strip()
    for trap_type, trap_info in TRAP_PATTERNS.items():
        for pattern in trap_info["patterns"]:
            if re.search(pattern, lower, re.IGNORECASE):
                return trap_type
    return None


def get_trap_response(trap_type: str, lang: str = "vi") -> str:
    """Get the appropriate rejection response for a trap question."""
    trap_info = TRAP_PATTERNS.get(trap_type)
    if not trap_info:
        if lang == "en":
            return "I cannot perform that action. I am a read-only assistant."
        return "Mình không thể thực hiện hành động đó. Mình là trợ lý chỉ đọc."

    key = "response_en" if lang == "en" else "response_vi"
    return trap_info[key]


def validate_response(text: str) -> str:
    """
    Validate AI response doesn't contain banned phrases.
    Returns cleaned text with violations removed/replaced.
    """
    result = text
    for phrase in BANNED_PHRASES_VI + BANNED_PHRASES_EN:
        if phrase.lower() in result.lower():
            result = re.sub(
                re.escape(phrase),
                "[đã xoá — không được phán chắc]",
                result,
                flags=re.IGNORECASE,
            )
    return result


def get_disclaimer(lang: str = "vi") -> str:
    """Get the mandatory disclaimer text."""
    return DISCLAIMER_EN if lang == "en" else DISCLAIMER_VI


def detect_language(message: str) -> str:
    """Simple language detection: Vietnamese vs English."""
    # Vietnamese-specific characters
    vn_chars = set("àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ")
    lower = message.lower()
    vn_count = sum(1 for c in lower if c in vn_chars)

    # Vietnamese keywords
    vn_keywords = ["tôi", "mình", "bạn", "chi", "giao dịch", "tài khoản", "sao kê",
                   "khoản", "phí", "tiền", "thẻ", "gói", "tháng", "năm", "có", "không",
                   "gửi", "báo cáo", "kiểm tra"]
    vn_keyword_count = sum(1 for kw in vn_keywords if kw in lower)

    if vn_count > 2 or vn_keyword_count >= 2:
        return "vi"
    return "en"
