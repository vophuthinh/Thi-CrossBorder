"""
Wealify Smart Finance — Streamlit Dashboard-First UI
Dashboard chính + Chat tab phụ
Powered by BytePlus Seed 2.0
"""
import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px

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

# ─── Color Palette ──────────────────────────────────────

COLORS = {
    "primary": "#e94560",
    "secondary": "#f39c12",
    "accent": "#00d2ff",
    "bg_dark": "#0f0f1a",
    "bg_card": "#1a1a2e",
    "bg_surface": "#16213e",
    "text": "#e0e0e0",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
}

# ─── Custom CSS ─────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #0a0a14; }

    /* Header */
    .hero-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 20px;
        padding: 28px 36px;
        margin-bottom: 24px;
        border: 1px solid rgba(233, 69, 96, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .hero-title {
        font-size: 32px;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #e94560, #f39c12, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        font-size: 14px;
        color: #8888aa;
        margin-top: 6px;
        letter-spacing: 0.3px;
    }

    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(233, 69, 96, 0.15), rgba(243, 156, 18, 0.15));
        border: 1px solid rgba(233, 69, 96, 0.3);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 11px;
        color: #f39c12;
        margin-top: 10px;
        font-weight: 600;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border-radius: 16px;
        padding: 20px 24px;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    }

    .metric-icon { font-size: 24px; margin-bottom: 8px; }

    .metric-label {
        font-size: 12px;
        color: #8888aa;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }

    .metric-value.green { color: #22c55e; }
    .metric-value.red { color: #ef4444; }
    .metric-value.yellow { color: #f59e0b; }
    .metric-value.blue { color: #3b82f6; }

    .metric-change {
        font-size: 11px;
        margin-top: 4px;
    }

    /* Risk gauge */
    .risk-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.06);
        text-align: center;
    }

    .risk-score {
        font-size: 48px;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .risk-label {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-top: 4px;
    }

    /* Section headers */
    .section-header {
        color: #e0e0e0;
        font-size: 18px;
        font-weight: 700;
        margin: 28px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(233, 69, 96, 0.3);
    }

    /* Anomaly items */
    .anomaly-item {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }

    .anomaly-item.warning {
        background: rgba(245, 158, 11, 0.08);
        border-color: rgba(245, 158, 11, 0.2);
    }

    .anomaly-item.info {
        background: rgba(59, 130, 246, 0.08);
        border-color: rgba(59, 130, 246, 0.2);
    }

    .anomaly-item.success {
        background: rgba(34, 197, 94, 0.08);
        border-color: rgba(34, 197, 94, 0.2);
    }

    /* Disclaimer */
    .disclaimer-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(243, 156, 18, 0.05));
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 14px 18px;
        margin-top: 24px;
        font-size: 12px;
        color: #d4a017;
        line-height: 1.6;
    }

    /* Sidebar */
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

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a2e;
        border-radius: 10px;
        padding: 8px 20px;
        color: #8888aa;
        border: 1px solid rgba(255,255,255,0.06);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e94560, #f39c12) !important;
        color: white !important;
    }

    /* Chat styling */
    .stChatMessage {
        border-radius: 16px !important;
    }

    /* Powered by badge */
    .powered-by {
        text-align: center;
        padding: 16px;
        color: #555;
        font-size: 12px;
    }

    .powered-by span {
        background: linear-gradient(90deg, #e94560, #f39c12);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# ─── API Helpers ─────────────────────────────────────────


def api_get(endpoint: str):
    """GET from backend API with error handling."""
    try:
        resp = requests.get(f"{API_URL}{endpoint}", timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def api_post(endpoint: str, data: dict):
    """POST to backend API with error handling."""
    try:
        resp = requests.post(f"{API_URL}{endpoint}", json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


# ─── Language ────────────────────────────────────────────

lang = st.session_state.get("lang", "vi")

# ─── Header ──────────────────────────────────────────────

st.markdown("""
<div class="hero-header">
    <div class="hero-title">🛡️ Wealify Smart Finance</div>
    <div class="hero-subtitle">AI Dashboard soi sao kê · Quản lý chi tiêu & An toàn giao dịch cho Seller Cross-Border</div>
    <div class="hero-badge">⚡ Powered by BytePlus Seed 2.0</div>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Settings")

    lang_choice = st.radio(
        "🌐 Ngôn ngữ / Language",
        ["Tiếng Việt", "English"],
        index=0 if lang == "vi" else 1,
    )
    st.session_state["lang"] = "vi" if lang_choice == "Tiếng Việt" else "en"
    lang = st.session_state["lang"]

    st.markdown("---")

    # Backend status
    health = api_get("/health")
    if health:
        st.success("🟢 Backend connected")
        if health.get("has_api_key"):
            st.info("🔑 BytePlus API key: ✅")
        else:
            st.warning("🔑 API key: demo mode")
    else:
        st.error("🔴 Backend offline — Run: `cd backend && python main.py`")

    st.markdown("---")

    if st.button("🔄 Refresh Data", use_container_width=True):
        api_post("/reset", {})
        st.cache_data.clear()
        st.rerun()

    if st.button("🔍 Rà soát định kỳ" if lang == "vi" else "🔍 Scheduled Scan", use_container_width=True):
        with st.spinner("Đang rà soát..." if lang == "vi" else "Scanning..."):
            check_result = api_post("/scheduled-check", {})
        if check_result:
            new_flags = check_result.get("new_flags", 0)
            skipped = check_result.get("already_reported", 0)
            risk = check_result.get("risk_score", {})
            st.success(
                f"✅ Hoàn tất! {new_flags} cảnh báo mới, {skipped} đã báo trước."
                if lang == "vi" else
                f"✅ Done! {new_flags} new flags, {skipped} already reported."
            )
            if risk:
                st.metric("Risk Score", f"{risk.get('total_score', 0)}/100", risk.get("level_vi", ""))
        else:
            st.error("Không thể chạy rà soát." if lang == "vi" else "Scan failed.")

    st.markdown("---")

    if st.button("📝 Xuất nhật ký" if lang == "vi" else "📝 Export Audit Log", use_container_width=True):
        export_result = api_get("/audit-log/export")
        if export_result:
            st.success(f"✅ Đã xuất: {export_result.get('exported_to', '')}")
        else:
            st.error("Export failed.")

    st.markdown("---")
    st.markdown(
        '<div class="powered-by">Built with <span>BytePlus Seed 2.0</span><br>'
        'AI Cross-Border Hackathon 2026</div>',
        unsafe_allow_html=True,
    )


# ─── Check backend connection ───────────────────────────

if not health:
    st.error(
        "⚠️ Không kết nối được backend. Chạy lệnh sau:\n\n"
        "```bash\ncd backend && python main.py\n```"
    )
    st.stop()


# ─── Load Dashboard Data ────────────────────────────────

@st.cache_data(ttl=60)
def load_overview():
    return api_get("/dashboard/overview")


@st.cache_data(ttl=60)
def load_anomalies():
    return api_get("/dashboard/anomalies")


@st.cache_data(ttl=60)
def load_reconciliation():
    return api_get("/dashboard/reconciliation")


@st.cache_data(ttl=60)
def load_risk_score():
    return api_get("/dashboard/risk-score")


@st.cache_data(ttl=60)
def load_email_matches():
    return api_get("/dashboard/email-matches")


@st.cache_data(ttl=60)
def load_transactions():
    return api_get("/dashboard/transactions")


overview = load_overview()
risk_data = load_risk_score()
anomalies = load_anomalies()

if not overview:
    st.error("Không tải được dữ liệu. Kiểm tra backend.")
    st.stop()


# ─── Metric Cards Row ───────────────────────────────────

summary = overview.get("summary", {})

# Extract values
total_in = 0
total_out = 0
total_fees = 0
txn_count = 0
net = 0

for k, v in summary.items():
    kl = k.lower()
    if "vào" in kl or "income" in kl:
        total_in = v
    elif "chi tiêu" in kl or "spending" in kl:
        total_out = v
    elif "phí" in kl or "fee" in kl:
        total_fees = v
    elif "ròng" in kl or "net" in kl:
        net = v
    elif "giao dịch" in kl or "count" in kl:
        txn_count = v

risk_score = risk_data.get("total_score", 0) if risk_data else 0
risk_level = risk_data.get("level_vi", "N/A") if risk_data else "N/A"
risk_color_class = "green"
if risk_score > 50:
    risk_color_class = "red"
elif risk_score > 20:
    risk_color_class = "yellow"

cols = st.columns(4)

with cols[0]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💰</div>
        <div class="metric-label">{"Tổng thu" if lang == "vi" else "Total Income"}</div>
        <div class="metric-value green">${total_in:,.2f}</div>
        <div class="metric-change" style="color: #22c55e;">↑ {"Tiền vào tài khoản" if lang == "vi" else "Money in"}</div>
    </div>
    """, unsafe_allow_html=True)

with cols[1]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💸</div>
        <div class="metric-label">{"Tổng chi" if lang == "vi" else "Total Spending"}</div>
        <div class="metric-value red">${total_out:,.2f}</div>
        <div class="metric-change" style="color: #ef4444;">↓ {"Chi tiêu + quẹt thẻ" if lang == "vi" else "Charges + purchases"}</div>
    </div>
    """, unsafe_allow_html=True)

with cols[2]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-label">{"Phí dịch vụ" if lang == "vi" else "Service Fees"}</div>
        <div class="metric-value yellow">${total_fees:,.2f}</div>
        <div class="metric-change" style="color: #f59e0b;">{txn_count} {"giao dịch" if lang == "vi" else "transactions"}</div>
    </div>
    """, unsafe_allow_html=True)

with cols[3]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🛡️</div>
        <div class="metric-label">Risk Score</div>
        <div class="metric-value {risk_color_class}">{risk_score}/100</div>
        <div class="metric-change" style="color: {risk_data.get('color', '#888') if risk_data else '#888'};">{risk_level}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)


# ─── Tabs ────────────────────────────────────────────────

tab_overview, tab_reconcile, tab_safety, tab_chat = st.tabs([
    "📊 Tổng quan" if lang == "vi" else "📊 Overview",
    "🔍 Đối chiếu" if lang == "vi" else "🔍 Reconciliation",
    "🛡️ An toàn" if lang == "vi" else "🛡️ Safety",
    "💬 Chat AI",
])


# ═══════════════════════════════════════════════════════
# TAB 1: TỔNG QUAN
# ═══════════════════════════════════════════════════════

with tab_overview:
    # AI Insight section
    st.markdown(
        f'<div class="section-header">🤖 {"AI Insight" if lang == "vi" else "AI Insight"}'
        f' <span style="font-size:11px;color:#888;font-weight:400;">'
        f'Powered by BytePlus Seed 2.0</span></div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Đang phân tích..." if lang == "vi" else "Analyzing..."):
        insight_data = api_post("/ai/insight", {"context": "general"})

    if insight_data:
        source_label = (
            "🟢 Live AI" if insight_data.get("source") == "byteplus_seed_2.0"
            else "🟡 Demo Mode"
        )
        st.markdown(
            f'<div class="anomaly-item info">'
            f'<div style="font-size:11px;color:#888;margin-bottom:8px;">{source_label} · {insight_data.get("powered_by", "")}</div>'
            f'{insight_data.get("insight", "")}'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Không tải được AI Insight.")

    # Charts row
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown(
            f'<div class="section-header">📈 '
            f'{"Thu chi theo tháng" if lang == "vi" else "Monthly Income vs Spending"}</div>',
            unsafe_allow_html=True,
        )
        monthly = overview.get("monthly_breakdown", {})
        if monthly:
            months = sorted(monthly.keys())
            incomes = [monthly[m].get("income", 0) for m in months]
            spendings = [monthly[m].get("spending", 0) for m in months]
            fees = [monthly[m].get("fees", 0) for m in months]

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                name="Thu nhập" if lang == "vi" else "Income",
                x=months, y=incomes,
                marker_color="#22c55e",
                marker_line_width=0,
            ))
            fig_bar.add_trace(go.Bar(
                name="Chi tiêu" if lang == "vi" else "Spending",
                x=months, y=spendings,
                marker_color="#ef4444",
                marker_line_width=0,
            ))
            fig_bar.add_trace(go.Bar(
                name="Phí" if lang == "vi" else "Fees",
                x=months, y=fees,
                marker_color="#f59e0b",
                marker_line_width=0,
            ))
            fig_bar.update_layout(
                barmode="group",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#aaa", family="Inter"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=40, r=20, t=20, b=40),
                height=320,
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickprefix="$"),
            )
            st.plotly_chart(fig_bar, use_container_width=True, key="bar_chart")

    with chart_col2:
        st.markdown(
            f'<div class="section-header">🍩 '
            f'{"Phân bổ giao dịch" if lang == "vi" else "Transaction Distribution"}</div>',
            unsafe_allow_html=True,
        )
        categories = overview.get("categories", {})
        if categories:
            cat_labels = {
                "payin": "Thu nhập" if lang == "vi" else "Income",
                "payout": "Rút tiền" if lang == "vi" else "Payout",
                "transfer": "Chuyển thẻ" if lang == "vi" else "Transfer",
                "fee": "Phí" if lang == "vi" else "Fee",
                "charge": "Chi tiêu" if lang == "vi" else "Charge",
            }
            labels = [cat_labels.get(k, k) for k in categories.keys()]
            values = list(categories.values())
            colors = ["#22c55e", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444"]

            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors[:len(labels)], line=dict(color="#0a0a14", width=2)),
                textinfo="percent+label",
                textfont=dict(size=11, color="#ddd"),
            )])
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#aaa", family="Inter"),
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=320,
            )
            st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")

    # Top 3 largest charges
    st.markdown(
        f'<div class="section-header">🏆 '
        f'{"Top 3 khoản lớn nhất" if lang == "vi" else "Top 3 Largest Charges"}</div>',
        unsafe_allow_html=True,
    )
    top3 = overview.get("top3_largest", [])
    if top3:
        top_cols = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]
        for i, t in enumerate(top3[:3]):
            with top_cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 20px;">{medals[i]}</div>
                    <div style="color: #fff; font-weight: 600; font-size: 14px; margin: 6px 0;">{t['description']}</div>
                    <div style="color: #ef4444; font-size: 22px; font-weight: 700;">${abs(t['amount']):,.2f}</div>
                    <div style="color: #888; font-size: 11px; margin-top: 4px;">📅 {t['date']}</div>
                </div>
                """, unsafe_allow_html=True)

    # Transaction table
    st.markdown(
        f'<div class="section-header">📋 '
        f'{"Bảng giao dịch" if lang == "vi" else "Transaction Table"}</div>',
        unsafe_allow_html=True,
    )
    txn_data = load_transactions()
    if txn_data:
        account_txns = txn_data.get("account_transactions", [])
        if account_txns:
            import pandas as pd
            df = pd.DataFrame(account_txns)
            display_cols = ["date", "description", "type", "amount", "balance"]
            available_cols = [c for c in display_cols if c in df.columns]
            df_display = df[available_cols].copy()
            if "amount" in df_display.columns:
                df_display["amount"] = df_display["amount"].apply(lambda x: f"${x:,.2f}")
            if "balance" in df_display.columns:
                df_display["balance"] = df_display["balance"].apply(lambda x: f"${x:,.2f}")
            col_names = {
                "date": "Ngày" if lang == "vi" else "Date",
                "description": "Mô tả" if lang == "vi" else "Description",
                "type": "Loại" if lang == "vi" else "Type",
                "amount": "Số tiền" if lang == "vi" else "Amount",
                "balance": "Số dư" if lang == "vi" else "Balance",
            }
            df_display = df_display.rename(columns=col_names)
            st.dataframe(df_display, use_container_width=True, height=300)

    # Quarterly & Yearly Report
    report_data = api_get("/dashboard/report")
    if report_data:
        q_col, y_col = st.columns(2)

        with q_col:
            st.markdown(
                f'<div class="section-header">📅 '
                f'{"Báo cáo theo quý" if lang == "vi" else "Quarterly Report"}</div>',
                unsafe_allow_html=True,
            )
            quarterly = report_data.get("quarterly_breakdown", {})
            if quarterly:
                for q_key, q_data in sorted(quarterly.items()):
                    net_color = "#22c55e" if q_data["net"] >= 0 else "#ef4444"
                    st.markdown(f"""
                    <div class="anomaly-item info" style="padding:10px 14px;">
                        <div style="font-weight:700;color:#fff;font-size:14px;">{q_key}</div>
                        <div style="display:flex;gap:16px;margin-top:6px;font-size:12px;">
                            <span style="color:#22c55e;">Thu: ${q_data['income']:,.2f}</span>
                            <span style="color:#ef4444;">Chi: ${q_data['spending']:,.2f}</span>
                            <span style="color:#f59e0b;">Phí: ${q_data['fees']:,.2f}</span>
                            <span style="color:{net_color};font-weight:700;">Ròng: ${q_data['net']:,.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with y_col:
            st.markdown(
                f'<div class="section-header">📆 '
                f'{"Báo cáo theo năm" if lang == "vi" else "Yearly Report"}</div>',
                unsafe_allow_html=True,
            )
            yearly = report_data.get("yearly_breakdown", {})
            if yearly:
                for y_key, y_data in sorted(yearly.items()):
                    net_color = "#22c55e" if y_data["net"] >= 0 else "#ef4444"
                    st.markdown(f"""
                    <div class="anomaly-item info" style="padding:10px 14px;">
                        <div style="font-weight:700;color:#fff;font-size:14px;">{y_key}</div>
                        <div style="display:flex;gap:16px;margin-top:6px;font-size:12px;">
                            <span style="color:#22c55e;">Thu: ${y_data['income']:,.2f}</span>
                            <span style="color:#ef4444;">Chi: ${y_data['spending']:,.2f}</span>
                            <span style="color:#f59e0b;">Phí: ${y_data['fees']:,.2f}</span>
                            <span style="color:{net_color};font-weight:700;">Ròng: ${y_data['net']:,.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Subscription projection
            subs = report_data.get("subscriptions", {})
            if subs:
                st.markdown(
                    f'<div class="section-header">📋 '
                    f'{"Gói đăng ký — Dự báo chi phí" if lang == "vi" else "Subscriptions — Cost Projection"}</div>',
                    unsafe_allow_html=True,
                )
                for label, val in subs.items():
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:4px 0;">
                        <span style="color:#bbb;font-size:13px;">{label}</span>
                        <span style="color:#fff;font-weight:600;font-size:13px;">{"$" + f"{val:,.2f}" if isinstance(val, float) else val}</span>
                    </div>
                    """, unsafe_allow_html=True)# ═══════════════════════════════════════════════════════
# TAB 2: ĐỐI CHIẾU
# ═══════════════════════════════════════════════════════

with tab_reconcile:
    recon = load_reconciliation()
    email_data = load_email_matches()

    if recon:
        n_disc = recon.get("total_discrepancies", 0)
        recon_summary = recon.get("summary", {})

        # Summary cards
        st.markdown(
            f'<div class="section-header">🔍 '
            f'{"Đối chiếu 3 nguồn: Tài khoản ↔ Thẻ ↔ Ví" if lang == "vi" else "3-Source Reconciliation: Account ↔ Card ↔ Wallet"}</div>',
            unsafe_allow_html=True,
        )

        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.metric(
                "Giao dịch TK" if lang == "vi" else "Account Txns",
                recon_summary.get("charges_on_account", 0),
            )
        with rc2:
            st.metric(
                "Giao dịch Thẻ" if lang == "vi" else "Card Txns",
                recon_summary.get("charges_on_card", 0),
            )
        with rc3:
            st.metric(
                "Chuyển khoản" if lang == "vi" else "Transfers",
                recon_summary.get("transfers_checked", 0),
                f"${recon_summary.get('total_transferred', 0):,.2f}",
            )
        with rc4:
            delta_color = "normal" if n_disc == 0 else "inverse"
            st.metric(
                "Khoản lệch" if lang == "vi" else "Discrepancies",
                n_disc,
                "✅ Khớp" if n_disc == 0 else f"⚠️ {n_disc} lệch",
                delta_color=delta_color,
            )

        # Discrepancy list
        if n_disc > 0:
            st.markdown(
                f'<div class="section-header">⚠️ '
                f'{"Chi tiết khoản lệch" if lang == "vi" else "Discrepancy Details"}</div>',
                unsafe_allow_html=True,
            )
            for disc in recon.get("discrepancies", []):
                disc_type = disc.get("type", "")
                icon = "🔴" if "duplicate" in disc_type else "🟡"
                css_class = "anomaly-item" if "duplicate" in disc_type else "anomaly-item warning"
                st.markdown(f"""
                <div class="{css_class}">
                    <div style="font-weight:600;color:#fff;font-size:14px;">
                        {icon} {disc.get('description', disc.get('type', ''))}
                    </div>
                    <div style="color:#bbb;font-size:13px;margin-top:4px;">
                        {disc.get('detail', '')}
                    </div>
                    <div style="color:#888;font-size:11px;margin-top:6px;">
                        Nguồn: {disc.get('source', '')}
                        {f" · Ref: {disc.get('reference', '')}" if disc.get('reference') else ""}
                        {f" · ${abs(disc.get('amount', 0)):,.2f}" if disc.get('amount') else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="anomaly-item success">
                <div style="font-weight:600;color:#22c55e;font-size:14px;">
                    ✅ Tất cả giao dịch khớp giữa 3 nguồn!
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Email matching section
    if email_data:
        st.markdown(
            f'<div class="section-header">📧 '
            f'{"Đối soát Email biên lai" if lang == "vi" else "Email Receipt Matching"}</div>',
            unsafe_allow_html=True,
        )
        email_summary = email_data.get("summary", {})
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            matched = email_summary.get("có_email_khớp", email_summary.get("matched_with_email", 0))
            st.metric("✅ Có email khớp" if lang == "vi" else "✅ Matched", matched)
        with ec2:
            no_email = email_summary.get("không_tìm_thấy_email", email_summary.get("no_email_found", 0))
            st.metric("❓ Không có email" if lang == "vi" else "❓ No email", no_email)
        with ec3:
            suspicious = email_summary.get("email_nghi_giả", email_summary.get("suspicious_email", 0))
            st.metric("🚨 Email nghi giả" if lang == "vi" else "🚨 Suspicious", suspicious)

        # Show suspicious matches
        matches = email_data.get("matches", [])
        suspicious_matches = [m for m in matches if m.get("match_status") == "suspicious_email"]
        if suspicious_matches:
            for m in suspicious_matches:
                reasons = m.get("suspicious_reasons", [])
                st.markdown(f"""
                <div class="anomaly-item">
                    <div style="font-weight:600;color:#ef4444;font-size:14px;">
                        🚨 {m.get('description', '')} — ${abs(m.get('amount', 0)):,.2f}
                    </div>
                    <div style="color:#bbb;font-size:13px;margin-top:4px;">
                        Email: {m.get('matched_email', {}).get('subject', '')}
                    </div>
                    <div style="color:#f59e0b;font-size:12px;margin-top:4px;">
                        ⚠️ {' · '.join(reasons)}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TAB 3: AN TOÀN
# ═══════════════════════════════════════════════════════

with tab_safety:
    if risk_data:
        # Risk Score Gauge
        st.markdown(
            f'<div class="section-header">🛡️ '
            f'{"Điểm rủi ro tổng hợp" if lang == "vi" else "Overall Risk Score"}</div>',
            unsafe_allow_html=True,
        )

        gauge_col, breakdown_col = st.columns([1, 1])

        with gauge_col:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                title={"text": f"Risk Level: {risk_level}", "font": {"size": 16, "color": "#aaa"}},
                number={"font": {"size": 56, "color": risk_data.get("color", "#fff")}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#555"},
                    "bar": {"color": risk_data.get("color", "#22c55e")},
                    "bgcolor": "#1a1a2e",
                    "bordercolor": "rgba(255,255,255,0.1)",
                    "steps": [
                        {"range": [0, 20], "color": "rgba(34, 197, 94, 0.15)"},
                        {"range": [20, 50], "color": "rgba(245, 158, 11, 0.15)"},
                        {"range": [50, 75], "color": "rgba(239, 68, 68, 0.15)"},
                        {"range": [75, 100], "color": "rgba(220, 38, 38, 0.15)"},
                    ],
                    "threshold": {
                        "line": {"color": "#fff", "width": 3},
                        "thickness": 0.8,
                        "value": risk_score,
                    },
                },
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#aaa", family="Inter"),
                height=280,
                margin=dict(l=30, r=30, t=40, b=20),
            )
            st.plotly_chart(fig_gauge, use_container_width=True, key="risk_gauge")

        with breakdown_col:
            st.markdown(
                f'<div class="section-header" style="margin-top:0;">📊 '
                f'{"Phân tích chi tiết" if lang == "vi" else "Score Breakdown"}</div>',
                unsafe_allow_html=True,
            )
            breakdown = risk_data.get("breakdown", {})
            for key, item in breakdown.items():
                score = item["score"]
                max_score = item["max"]
                pct = score / max_score * 100 if max_score else 0
                detail = item.get("detail" if lang == "vi" else "detail_en", "")

                bar_color = "#22c55e" if pct < 30 else ("#f59e0b" if pct < 60 else "#ef4444")
                label_map = {
                    "anomalies": "🔍 Khoản bất thường" if lang == "vi" else "🔍 Anomalies",
                    "discrepancies": "📊 Lệch 3 nguồn" if lang == "vi" else "📊 Discrepancies",
                    "suspicious_emails": "📧 Email nghi giả" if lang == "vi" else "📧 Suspicious Emails",
                    "price_hikes": "💰 Tăng giá" if lang == "vi" else "💰 Price Hikes",
                }

                st.markdown(f"""
                <div style="margin-bottom:14px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span style="color:#ddd;font-size:13px;font-weight:500;">{label_map.get(key, key)}</span>
                        <span style="color:{bar_color};font-size:13px;font-weight:700;">{score}/{max_score}</span>
                    </div>
                    <div style="background:#1a1a2e;border-radius:6px;height:8px;overflow:hidden;">
                        <div style="background:{bar_color};height:100%;width:{pct}%;border-radius:6px;transition:width 0.5s;"></div>
                    </div>
                    <div style="color:#888;font-size:11px;margin-top:3px;">{detail}</div>
                </div>
                """, unsafe_allow_html=True)

    # Subscriptions section
    if anomalies:
        subs = anomalies.get("subscriptions", [])
        if subs:
            st.markdown(
                f'<div class="section-header">📋 '
                f'{"Gói đăng ký đang hoạt động" if lang == "vi" else "Active Subscriptions"}</div>',
                unsafe_allow_html=True,
            )
            for sub in subs:
                st.markdown(f"""
                <div class="anomaly-item info">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <div style="font-weight:600;color:#fff;font-size:14px;">{sub['description']}</div>
                            <div style="color:#888;font-size:12px;margin-top:2px;">{sub.get('explanation', '')}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="color:#3b82f6;font-size:18px;font-weight:700;">${sub['current_price']:,.2f}</div>
                            <div style="color:#888;font-size:11px;">/{sub['frequency']}</div>
                        </div>
                    </div>
                    <div style="color:#666;font-size:11px;margin-top:6px;">
                        Kỳ kế tiếp: {sub['next_charge_date']} · {sub['occurrences']} lần · Label: {sub['label']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Price hikes
        hikes = anomalies.get("price_hikes", [])
        if hikes:
            st.markdown(
                f'<div class="section-header">⚠️ '
                f'{"Gói tăng giá âm thầm" if lang == "vi" else "Silent Price Increases"}</div>',
                unsafe_allow_html=True,
            )
            for h in hikes:
                st.markdown(f"""
                <div class="anomaly-item warning">
                    <div style="font-weight:600;color:#f59e0b;font-size:14px;">
                        ⚠️ {h['merchant']}
                    </div>
                    <div style="color:#fff;font-size:16px;margin-top:4px;">
                        ${h['old_price']:.2f} → ${h['new_price']:.2f}
                        <span style="color:#ef4444;font-size:13px;font-weight:600;">
                            (+${h['increase']:.2f}, +{h['increase_pct']}%)
                        </span>
                    </div>
                    <div style="color:#888;font-size:12px;margin-top:4px;">
                        {h.get('explanation', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Duplicates
        dupes = anomalies.get("duplicate_charges", [])
        if dupes:
            st.markdown(
                f'<div class="section-header">🔁 '
                f'{"Khoản trùng lặp" if lang == "vi" else "Duplicate Charges"}</div>',
                unsafe_allow_html=True,
            )
            for d in dupes:
                st.markdown(f"""
                <div class="anomaly-item">
                    <div style="font-weight:600;color:#ef4444;font-size:14px;">
                        🔁 {d['description']} — ${abs(d['amount']):,.2f}
                    </div>
                    <div style="color:#bbb;font-size:12px;margin-top:4px;">
                        Ngày: {d['date']} · Trùng với: {d.get('duplicate_of', 'N/A')}
                    </div>
                    <div style="color:#f59e0b;font-size:11px;margin-top:4px;">
                        Hạn khiếu nại: {d.get('dispute_deadline', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Unknown merchants
        unknowns = anomalies.get("unknown_merchants", [])
        if unknowns:
            st.markdown(
                f'<div class="section-header">❓ '
                f'{"Khoản lạ chưa xác định" if lang == "vi" else "Unknown Merchants"}</div>',
                unsafe_allow_html=True,
            )
            for u in unknowns:
                st.markdown(f"""
                <div class="anomaly-item warning">
                    <div style="font-weight:600;color:#f59e0b;font-size:14px;">
                        ❓ {u['description']} — ${abs(u['amount']):,.2f}
                    </div>
                    <div style="color:#bbb;font-size:12px;margin-top:4px;">
                        Mã: {u.get('merchant_code', 'N/A')} · Ngày: {u['date']}
                    </div>
                    <div style="color:#888;font-size:11px;margin-top:4px;">
                        {u.get('explanation', '')} · Hạn khiếu nại: {u.get('dispute_deadline', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TAB 4: CHAT AI
# ═══════════════════════════════════════════════════════

with tab_chat:
    st.markdown(
        f'<div class="section-header">💬 '
        f'{"Trợ lý AI — hỏi bất kỳ điều gì về tài khoản" if lang == "vi" else "AI Assistant — ask anything about your account"}</div>',
        unsafe_allow_html=True,
    )

    # Quick question buttons
    quick_questions = {
        "vi": [
            ("📊 Tổng chi tháng này", "Tháng này tôi chi bao nhiêu, phí bao nhiêu, 3 khoản lớn nhất là gì?"),
            ("📧 Đối soát email", "Đối soát giao dịch với email biên lai"),
            ("🔍 Đối chiếu 3 nguồn", "Có tiền nào rời tài khoản mà chưa thấy lên thẻ không?"),
            ("📋 Gói đăng ký", "Mình đang có những gói đăng ký định kỳ nào, gói nào vừa tăng giá?"),
            ("🔁 Khoản trùng", "Có khoản nào bị tính hai lần / phí kép không?"),
            ("📧 Gửi báo cáo", "Gửi báo cáo tháng này vào email của tôi"),
            ("⏰ Nhắc hạn 60 ngày", "Khoản nào sắp hết hạn khiếu nại 60 ngày?"),
            ("🔍 Rà soát toàn bộ", "Chạy kiểm tra toàn bộ tài khoản"),
            ("📝 Nhật ký cảnh báo", "Xem lịch sử cảnh báo đã ghi nhận"),
        ],
        "en": [
            ("📊 Monthly overview", "How much did I spend this month? What are the top 3 charges?"),
            ("📧 Email cross-check", "Cross-check transactions with email receipts"),
            ("🔍 3-source reconcile", "Any money left the account but hasn't reached the card?"),
            ("📋 Subscriptions", "What subscriptions do I have? Any price increases?"),
            ("🔁 Duplicates", "Are there any duplicate charges or double fees?"),
            ("📧 Send report", "Send the monthly report to my email"),
            ("⏰ Dispute deadlines", "Any items approaching the 60-day dispute deadline?"),
            ("🔍 Full scan", "Run a complete check on my account"),
            ("📝 Audit log", "Show the flag history"),
        ],
    }

    qcols = st.columns(3)
    for i, (label, question) in enumerate(quick_questions.get(lang, quick_questions["vi"])):
        with qcols[i % 3]:
            if st.button(label, key=f"chat_q_{label}", use_container_width=True):
                st.session_state["pending_question"] = question

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        welcome = (
            "👋 Xin chào! Mình là **trợ lý rà soát tài chính Wealify**.\n\n"
            "Bạn đã xem Dashboard — giờ hãy hỏi mình bất kỳ điều gì chi tiết hơn!"
        ) if lang == "vi" else (
            "👋 Hello! I'm your **Wealify financial assistant**.\n\n"
            "You've seen the Dashboard — now ask me anything for more details!"
        )
        st.session_state["messages"] = [{"role": "assistant", "content": welcome}]

    # Display chat history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"], avatar="🛡️" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Handle pending quick question
    pending = st.session_state.pop("pending_question", None)
    if pending:
        st.session_state["messages"].append({"role": "user", "content": pending})
        with st.chat_message("user", avatar="👤"):
            st.markdown(pending)

        with st.chat_message("assistant", avatar="🛡️"):
            with st.spinner("Đang phân tích..." if lang == "vi" else "Analyzing..."):
                data = api_post("/chat", {"message": pending})
                response_text = data.get("response", "Có lỗi xảy ra.") if data else "⚠️ Backend offline"

            st.markdown(response_text)

        st.session_state["messages"].append({"role": "assistant", "content": response_text})
        st.rerun()

    # Chat input
    user_input = st.chat_input(
        "Hỏi về sao kê, gói đăng ký, khoản lạ..." if lang == "vi" else "Ask about statements, subscriptions..."
    )

    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🛡️"):
            with st.spinner("Đang phân tích..." if lang == "vi" else "Analyzing..."):
                data = api_post("/chat", {"message": user_input})
                response_text = data.get("response", "Có lỗi xảy ra.") if data else "⚠️ Backend offline"

            st.markdown(response_text)

        st.session_state["messages"].append({"role": "assistant", "content": response_text})
        st.rerun()


# ─── Disclaimer (always visible) ────────────────────────

disclaimer = DISCLAIMER_VI if lang == "vi" else DISCLAIMER_EN
st.markdown(f'<div class="disclaimer-box">{disclaimer}</div>', unsafe_allow_html=True)
