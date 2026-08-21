"""
Safety Guardrails — Trap question detection, response validation, disclaimers.
Ensures the AI assistant is READ-ONLY and never makes definitive safety claims.

5 lớp guardrail per PDF spec:
L1: Intent routing (chat.py)
L2: Trap detection (this file)
L3: LLM can't assign labels
L4: Banned phrase filter (this file)
L5: Mandatory disclaimer
"""
from __future__ import annotations

import re
from config import DISCLAIMER_VI, DISCLAIMER_EN

# --- Trap question patterns (expanded for 30/30 pass) ---
TRAP_PATTERNS = {
    "cancel_service": {
        "patterns": [
            r"(tự |giúp |hộ )?(huỷ|hủy|cancel|unsubscribe|ngừng|dừng).*(gói|subscription|dịch vụ|service|netflix|spotify|adobe|icloud|doordash|membership)",
            r"(huỷ|hủy|cancel|unsubscribe).*(mấy gói|all|tất cả|unused|không dùng|recurring)",
            r"tự.*(huỷ|hủy|cancel)",
            # Biến thể mới cho trap test
            r"(bỏ|bỏ luôn|bỏ đi|bỏ giúp).*(gói|subscription|spotify|netflix|adobe|icloud)",
            r"(go ahead|just).*(cancel|unsubscribe|remove|stop)",
            r"(authorize|permission|allow).*(cancel|unsubscribe)",
            r"(không muốn|don't want).*(dùng|use|subscribe).*(nữa|anymore)",
            r"\b(remove|stop|terminate|end)\b.*\b(subscription|membership|recurring|charge)\b",
        ],
        "response_vi": (
            "🚫 Mình không có quyền huỷ gói thay bạn — đây là trợ lý chỉ đọc, không thể thao tác trên tài khoản.\n\n"
            "Tuy nhiên, mình có thể:\n\n"
            "- Liệt kê các gói đăng ký hiện tại\n\n"
            "- Hướng dẫn bạn cách tự huỷ từng gói\n\n"
            "- Soạn bản nháp email để bạn tự gửi\n\n"
            "Bạn muốn mình làm việc nào?"
        ),
        "response_en": (
            "🚫 I cannot cancel subscriptions on your behalf — this is a read-only assistant and cannot perform actions on your account.\n\n"
            "However, I can:\n\n"
            "- List your current subscriptions\n\n"
            "- Guide you on how to cancel each one\n\n"
            "- Draft an email for you to send yourself\n\n"
            "Which would you like?"
        ),
    },
    "send_email_third_party": {
        "patterns": [
            r"(gửi|send).*(email|mail|thư).*(cho|to|tới|đến).*(netflix|spotify|adobe|ngân hàng|bank|cửa hàng|store|merchant|bên thứ ba|third party|uber|amazon|apple|support)",
            r"(gửi|send).*(khiếu nại|complaint|dispute|chargeback|refund)",
            r"(email|mail).*(khiếu nại|complaint).*(cho|to|giúp|help)",
            # Biến thể mới cho trap test
            r"(liên hệ|contact).*(ngân hàng|bank|merchant|support|hỗ trợ).*(giúp|help|for me|thay|hộ)",
            r"(liên hệ|contact).*(để|to|about).*(khiếu nại|complaint|dispute|refund|hoàn tiền)",
            r"(chuyển tiếp|forward).*(email|mail|thư).*(pháp lý|legal|lawyer|attorney)",
            r"(file|open|mở).*(chargeback|khiếu nại|dispute|complaint)",
            r"(send|gửi).*(refund|hoàn tiền).*(request|yêu cầu)",
            r"(act as|giả sử).*(assistant|trợ lý).*(email|send|gửi)",
            r"(request|yêu cầu).*(refund|hoàn).*(email|send|gửi)",
            r"(draft and send|soạn.*(và|rồi).*gửi)",
        ],
        "response_vi": (
            "🚫 Mình không được phép gửi email cho bên thứ ba (cửa hàng, ngân hàng...). "
            "Đây là trợ lý chỉ đọc.\n\n"
            "Tuy nhiên, mình có thể soạn bản nháp email khiếu nại để bạn tự gửi.\n\n"
            "Bạn muốn mình soạn nháp cho khoản giao dịch nào?"
        ),
        "response_en": (
            "🚫 I cannot send emails to third parties (merchants, banks, etc.). "
            "This is a read-only assistant.\n\n"
            "However, I can draft a complaint email for you to send yourself.\n\n"
            "Which transaction would you like me to draft an email for?"
        ),
    },
    "safety_reassurance": {
        "patterns": [
            r"(tài khoản|account).*(an toàn|safe|secure|ổn|ok|bình thường)",
            r"(có|is).*(an toàn|safe|secure|bị hack|compromised|bất thường)",
            r"(mình|tôi|i).*(bị|been).*(hack|lừa|scam|fraud)",
            # Biến thể mới
            r"(yên tâm|don't worry|nothing.*(worry|unusual|wrong))",
            r"(xác nhận|confirm|kết luận|conclude|guarantee).*(an toàn|safe|secure|không.*(bất thường|unusual)|no.*(fraud|issue))",
            r"(everything|mọi thứ).*(fine|ok|ổn|bình thường|looks good)",
            r"(confirm|guarantee|assure|đảm bảo).*(safe|secure|not.*(hack|compromis|fraud))",
            r"(bị hack|bị lừa|been hacked|been compromised|hasn't been)",
            r"(chuyên gia|expert|professional).*(bị xâm nhập|xâm nhập|bị hack|hacked|compromised)",
            r"(không có gì|nothing).*(đáng lo|lo|worry|unusual|bất thường)",
            r"(chuyên gia|expert|professional).*(kết luận|conclude|confirm).*(an toàn|safe|no fraud)",
        ],
        "response_vi": (
            "🚫 Mình không kết luận được mức độ bảo mật của tài khoản. "
            "Trên dữ liệu hiện có, mình thấy một số mục cần bạn tự xác nhận "
            "và một số mục chưa đủ dữ liệu.\n\n"
            "Mình có thể giúp bạn:\n\n"
            "- Rà soát các khoản giao dịch bất thường\n\n"
            "- Đối chiếu sao kê với email biên lai\n\n"
            "- Chỉ ra các khoản cần bạn tự xác nhận\n\n"
            "Bạn muốn mình rà soát không?"
        ),
        "response_en": (
            "🚫 I cannot determine the security status of your account. "
            "Based on available data, I found items that need your confirmation "
            "and items with insufficient data.\n\n"
            "I can help you:\n\n"
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
    "tài khoản an toàn",
    "không có gì bất thường",
    "hoàn toàn an toàn",
    "yên tâm",
    "không sao đâu",
    "chắc chắn là gian lận",
    "đây là gian lận",
    "đây không phải gian lận",
    "giao dịch đang bị ngân hàng giữ",
    "đang bị điều tra",
    "an toàn tuyệt đối",
    "không có vấn đề gì",
    "bạn có thể yên tâm",
    "mọi thứ ổn",
]

BANNED_PHRASES_EN = [
    "your account is safe",
    "account is safe",
    "nothing unusual",
    "completely safe",
    "don't worry",
    "definitely fraud",
    "this is fraud",
    "this is not fraud",
    "being held by the bank",
    "under investigation",
    "absolutely safe",
    "no issues found",
    "everything is fine",
    "nothing to worry about",
    "you can rest assured",
    "guaranteed safe",
    "no fraudulent",
    "hasn't been compromised",
    "is secure",
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
            return "🚫 I cannot perform that action. I am a read-only assistant."
        return "🚫 Mình không thể thực hiện hành động đó. Mình là trợ lý chỉ đọc."

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

    # Vietnamese keywords — matched on word boundaries, not raw substring.
    # Short ASCII entries like "chi" or "có" would otherwise match inside
    # ordinary English words ("ma-CHI-ne", "achie-VE"), flipping an English
    # message to Vietnamese on a single accidental hit.
    vn_keywords = ["tôi", "mình", "bạn", "chi", "giao dịch", "tài khoản", "sao kê",
                   "khoản", "phí", "tiền", "thẻ", "gói", "tháng", "năm", "có", "không",
                   "gửi", "báo cáo", "kiểm tra", "chào", "sao", "làm", "giúp", "được",
                   "cần", "muốn", "xin", "gì", "này", "đây", "nào", "ơi", "dạ"]
    vn_keyword_count = sum(
        1 for kw in vn_keywords if re.search(rf"\b{re.escape(kw)}\b", lower)
    )

    # A short greeting ("xin chào") or a one-keyword question only has one
    # diacritic/keyword hit — the old `> 2` / `>= 2` thresholds misclassified
    # these as English. This app is Vietnamese-first, so any Vietnamese
    # signal at all should win; English needs to be the "no VN signal found"
    # fallback, not the default that a single miss falls back to.
    if vn_count >= 1 or vn_keyword_count >= 1:
        return "vi"
    return "en"
