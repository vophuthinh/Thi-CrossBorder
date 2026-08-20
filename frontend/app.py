"""
Wealify Smart Finance — Streamlit Chat UI
Trợ lý AI soi sao kê: Quản lý chi tiêu & an toàn giao dịch
"""
import streamlit as st
import requests
import json

# --- Page Config ---
st.set_page_config(
    page_title="Wealify Smart Finance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

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

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .disclaimer-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #f0c040;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        font-size: 13px;
        color: #856404;
        line-height: 1.5;
    }

    .stChatMessage {
        border-radius: 16px !important;
    }

    .header-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 20px;
        color: white;
    }

    .header-title {
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(90deg, #e94560, #f39c12, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .header-subtitle {
        font-size: 14px;
        color: #a0a0c0;
        margin-top: 4px;
    }

    .sidebar-section {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }

    .quick-btn {
        width: 100%;
        margin-bottom: 8px;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }

    div[data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }

    div[data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #e94560 0%, #f39c12 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 10px 16px;
        font-weight: 600;
        transition: transform 0.2s;
    }

    div[data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# --- Header (always visible, can't be hidden) ---
st.markdown("""
<div class="header-container">
    <div class="header-title">🛡️ Wealify Smart Finance</div>
    <div class="header-subtitle">Trợ lý AI soi sao kê · Quản lý chi tiêu & An toàn giao dịch</div>
</div>
""", unsafe_allow_html=True)

# --- Mandatory Disclaimer (CANNOT be hidden per requirements) ---
lang = st.session_state.get("lang", "vi")
disclaimer = DISCLAIMER_VI if lang == "vi" else DISCLAIMER_EN
st.markdown(f'<div class="disclaimer-box">{disclaimer}</div>', unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    # Language toggle
    lang_choice = st.radio(
        "🌐 Ngôn ngữ / Language",
        ["Tiếng Việt", "English"],
        index=0 if lang == "vi" else 1,
    )
    st.session_state["lang"] = "vi" if lang_choice == "Tiếng Việt" else "en"

    st.markdown("---")
    st.markdown("### 💡 Câu hỏi gợi ý" if lang == "vi" else "### 💡 Quick Actions")

    quick_questions = {
        "vi": [
            ("📊 Tổng chi tháng này", "Tháng này tôi chi bao nhiêu, phí bao nhiêu, 3 khoản lớn nhất là gì?"),
            ("📧 Đối soát email", "Đối soát giao dịch với email biên lai"),
            ("🔍 Đối chiếu 3 nguồn", "Có tiền nào rời tài khoản mà chưa thấy lên thẻ không?"),
            ("📋 Gói đăng ký", "Mình đang có những gói đăng ký định kỳ nào, gói nào vừa tăng giá?"),
            ("🔁 Khoản trùng", "Có khoản nào bị tính hai lần / phí kép không?"),
            ("📧 Gửi báo cáo", "Gửi báo cáo tháng này vào email của tôi"),
            ("❓ Tra $9.99", "Khoản $9.99 này là gì — có email xác nhận nào khớp không?"),
        ],
        "en": [
            ("📊 Monthly overview", "How much did I spend this month? What are the top 3 charges?"),
            ("📧 Email cross-check", "Cross-check transactions with email receipts"),
            ("🔍 3-source reconcile", "Any money left the account but hasn't reached the card?"),
            ("📋 Subscriptions", "What subscriptions do I have? Any price increases?"),
            ("🔁 Duplicates", "Are there any duplicate charges or double fees?"),
            ("📧 Send report", "Send the monthly report to my email"),
            ("❓ Lookup $9.99", "What is this $9.99 charge — any matching receipt?"),
        ],
    }

    for label, question in quick_questions.get(lang, quick_questions["vi"]):
        if st.button(label, key=f"q_{label}", use_container_width=True):
            st.session_state["pending_question"] = question

    st.markdown("---")
    st.markdown("### 📝 Nhật ký" if lang == "vi" else "### 📝 Audit Log")

    if st.button("📋 Xem nhật ký" if lang == "vi" else "📋 View Log", use_container_width=True):
        st.session_state["pending_question"] = "Xem nhật ký cảnh báo" if lang == "vi" else "Show audit log"

    if st.button("🗑️ Reset phiên" if lang == "vi" else "🗑️ Reset Session", use_container_width=True):
        try:
            requests.post(f"{API_URL}/reset", timeout=5)
        except Exception:
            pass
        st.session_state["messages"] = []
        st.rerun()

# --- Initialize chat history ---
if "messages" not in st.session_state:
    welcome = (
        "👋 Xin chào! Mình là **trợ lý rà soát tài chính Wealify**.\n\n"
        "Mình có thể giúp bạn:\n"
        "• 📊 **Tổng quan chi tiêu** — phân loại dòng tiền\n"
        "• 📧 **Đối soát email** — khớp giao dịch với biên lai\n"
        "• 🔍 **Đối chiếu 3 nguồn** — tài khoản ↔ ví ↔ thẻ\n"
        "• 📋 **Gói đăng ký** — tìm gói quên huỷ, tăng giá\n"
        "• 🔁 **Phát hiện trùng** — khoản tính 2 lần, phí kép\n"
        "• 📧 **Gửi báo cáo** — soạn email cho bạn xác nhận\n\n"
        "Hãy hỏi mình bất cứ điều gì về tài khoản của bạn!"
    ) if lang == "vi" else (
        "👋 Hello! I'm your **Wealify financial review assistant**.\n\n"
        "I can help you with:\n"
        "• 📊 **Spending overview** — categorize cash flows\n"
        "• 📧 **Email cross-check** — match transactions to receipts\n"
        "• 🔍 **3-source reconciliation** — account ↔ wallet ↔ card\n"
        "• 📋 **Subscriptions** — find forgotten subscriptions, price hikes\n"
        "• 🔁 **Duplicate detection** — double charges, duplicate fees\n"
        "• 📧 **Send report** — draft email for your confirmation\n\n"
        "Ask me anything about your account!"
    )
    st.session_state["messages"] = [{"role": "assistant", "content": welcome}]

# --- Display chat history ---
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"], avatar="🛡️" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# --- Handle pending quick question ---
pending = st.session_state.pop("pending_question", None)
if pending:
    st.session_state["messages"].append({"role": "user", "content": pending})
    with st.chat_message("user", avatar="👤"):
        st.markdown(pending)

    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("Đang phân tích..." if lang == "vi" else "Analyzing..."):
            try:
                resp = requests.post(
                    f"{API_URL}/chat",
                    json={"message": pending},
                    timeout=30,
                )
                data = resp.json()
                response_text = data.get("response", "Có lỗi xảy ra." if lang == "vi" else "An error occurred.")
            except requests.exceptions.ConnectionError:
                response_text = ("⚠️ Không kết nối được backend. Hãy chạy `cd backend && python3 main.py` trước."
                                if lang == "vi"
                                else "⚠️ Cannot connect to backend. Please run `cd backend && python3 main.py` first.")
            except Exception as e:
                response_text = f"⚠️ Error: {str(e)}"

        st.markdown(response_text)

    st.session_state["messages"].append({"role": "assistant", "content": response_text})
    st.rerun()

# --- Chat input ---
user_input = st.chat_input(
    "Hỏi về sao kê, gói đăng ký, khoản lạ..." if lang == "vi" else "Ask about statements, subscriptions, suspicious charges..."
)

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("Đang phân tích..." if lang == "vi" else "Analyzing..."):
            try:
                resp = requests.post(
                    f"{API_URL}/chat",
                    json={"message": user_input},
                    timeout=30,
                )
                data = resp.json()
                response_text = data.get("response", "Có lỗi xảy ra." if lang == "vi" else "An error occurred.")
            except requests.exceptions.ConnectionError:
                response_text = ("⚠️ Không kết nối được backend. Hãy chạy `cd backend && python3 main.py` trước."
                                if lang == "vi"
                                else "⚠️ Cannot connect to backend. Please run `cd backend && python3 main.py` first.")
            except Exception as e:
                response_text = f"⚠️ Error: {str(e)}"

        st.markdown(response_text)

    st.session_state["messages"].append({"role": "assistant", "content": response_text})
    st.rerun()
