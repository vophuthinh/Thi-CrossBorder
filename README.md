# 🛡️ Wealify Smart Finance
### AI-powered Dashboard for Expense Management & Transaction Safety — Cross-Border Sellers

> **WLF-01** — AI Cross-Border Hackathon 2026  
> Built with **BytePlus Seed 2.0** × **Wealify**

---

## 🎯 Bài toán

Seller cross-border e-commerce (Etsy, Amazon, TikTok Shop) gặp khó khăn:
- **Chi tiêu phân tán**: Quảng cáo, shipping, COGS, phí sàn — mỗi nơi một nền tảng
- **Không biết ROI thật**: Chi $500 quảng cáo nhưng không biết lãi hay lỗ
- **Rủi ro giao dịch**: Fraud, phí ẩn, duplicate charges, unauthorized access
- **Dòng tiền bất ổn**: Tiền về không đều, dễ hụt vốn

## 💡 Giải pháp

**AI Dashboard** phân tích toàn diện tài chính seller qua **multi-agent pipeline** chuyên biệt:

### 7 AI Agents

| # | Agent | Chức năng |
|---|---|---|
| 1 | 📄 **Statement Parser** | Đọc & phân loại sao kê tài khoản |
| 2 | 📧 **Email Matcher** | Đối soát giao dịch với email biên lai |
| 3 | 🔍 **Reconciler** | Đối chiếu 3 nguồn: Account ↔ Card ↔ Wallet |
| 4 | 🚨 **Anomaly Detector** | Phát hiện khoản bất thường, gói quên huỷ, tăng giá |
| 5 | 📊 **Report Generator** | Báo cáo tài chính tổng hợp |
| 6 | ✉️ **Email Drafter** | Soạn email báo cáo (chờ user xác nhận) |
| 7 | 🛡️ **Risk Scorer** | Tính Risk Score 0-100 |

### Dashboard 4 Tab

| Tab | Nội dung |
|---|---|
| 📊 **Tổng quan** | Metric cards, charts thu/chi, phân bổ giao dịch, AI Insight |
| 🔍 **Đối chiếu** | 3-source reconciliation, email matching |
| 🛡️ **An toàn** | Risk gauge, gói đăng ký, tăng giá, khoản trùng |
| 💬 **Chat AI** | Chatbot hỏi đáp chi tiết |

## 🏗️ Architecture

```
Input: Dữ liệu giao dịch seller (CSV + Email + JSON)
      ↓
┌──────────────┬──────────────┬──────────────┬──────────────┐
│  Agent 1-2    │   Agent 3     │   Agent 4     │   Agent 7     │
│  PARSE +      │   RECONCILE   │   ANOMALY     │   RISK        │
│  MATCH EMAIL  │   3 nguồn     │   DETECT      │   SCORER      │
└──────────────┴──────────────┴──────────────┴──────────────┘
      ↓
   Dashboard (Streamlit + Plotly) + AI Insight (BytePlus Seed 2.0)
```

**Tech Stack:**
- **Backend**: Python + FastAPI
- **AI**: BytePlus Seed 2.0 (Omni — multi-modal LLM)
- **Frontend**: Streamlit + Plotly (Dashboard-first)
- **Safety**: Guardrails, trap detection, mandatory disclaimers
- **Design**: Dashboard-first (không phải chatbot)

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/vophuthinh/Thi-CrossBorder.git
cd Thi-CrossBorder
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Sửa .env: thêm BYTEPLUS_API_KEY + BYTEPLUS_ENDPOINT
python main.py
# → API running at http://localhost:8000
```

### 3. Frontend
```bash
cd frontend
pip install -r requirements.txt
python -m streamlit run app.py
# → Dashboard at http://localhost:8501
```

### 4. Demo
1. Mở Dashboard → Tab **📊 Tổng quan** → xem metrics + charts
2. Tab **🔍 Đối chiếu** → xem khoản lệch giữa 3 nguồn
3. Tab **🛡️ An toàn** → xem Risk Score + gói đăng ký
4. Tab **💬 Chat AI** → hỏi chi tiết

## 📊 Demo Features

| Feature | Mô tả |
|---|---|
| 4 Metric Cards | Tổng thu, tổng chi, phí, Risk Score |
| Bar Chart | Thu/chi theo tháng (Plotly) |
| Donut Chart | Phân bổ giao dịch theo loại |
| Risk Gauge | Điểm rủi ro 0-100 với breakdown |
| 3-Source Reconciliation | Đối chiếu Account ↔ Card ↔ Wallet |
| Email Matching | Tự động khớp giao dịch với biên lai email |
| Subscription Tracking | Phát hiện gói quên huỷ, tăng giá âm thầm |
| AI Insight | BytePlus Seed 2.0 phân tích & gợi ý |
| Song ngữ | Tiếng Việt / English |

## 🔑 Environment Variables

```env
BYTEPLUS_ENDPOINT=your_endpoint_id_here
BYTEPLUS_API_KEY=your_key_here
LLM_PROVIDER=byteplus    # byteplus | openai | anthropic
DEMO_MODE=true            # true = cached data, false = live API
```

## 📁 Project Structure

```
hackathon/
├── backend/
│   ├── main.py                     # FastAPI app (8 dashboard endpoints)
│   ├── agents/
│   │   ├── statement_parser.py     # Agent 1: Parse sao kê
│   │   ├── email_matcher.py        # Agent 2: Đối soát email
│   │   ├── reconciler.py           # Agent 3: Đối chiếu 3 nguồn
│   │   ├── anomaly_detector.py     # Agent 4: Phát hiện bất thường
│   │   ├── report_generator.py     # Agent 5: Báo cáo
│   │   ├── email_drafter.py        # Agent 6: Soạn email
│   │   └── risk_scorer.py          # Agent 7: Risk Score
│   ├── chat.py                     # Chat orchestrator
│   ├── llm_client.py               # BytePlus Seed 2.0 wrapper
│   ├── safety.py                   # Guardrails & trap detection
│   ├── data_loader.py              # Data parsing + masking
│   ├── audit_log.py                # Audit trail
│   ├── config.py                   # Configuration
│   └── requirements.txt
├── frontend/
│   ├── app.py                      # Streamlit Dashboard (4 tabs)
│   └── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ API Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/health` | Health check + model info |
| GET | `/dashboard/overview` | Tổng quan tài chính |
| GET | `/dashboard/transactions` | Bảng giao dịch |
| GET | `/dashboard/anomalies` | Khoản bất thường |
| GET | `/dashboard/reconciliation` | Đối chiếu 3 nguồn |
| GET | `/dashboard/email-matches` | Đối soát email |
| GET | `/dashboard/risk-score` | Risk Score 0-100 |
| GET | `/dashboard/report` | Báo cáo tổng hợp |
| POST | `/ai/insight` | AI Insight (BytePlus Seed 2.0) |
| POST | `/chat` | Chat AI |

## 🛡️ Safety Features

- **Trap Question Detection**: Từ chối yêu cầu huỷ gói, gửi email bên thứ 3, kết luận an toàn
- **Response Validation**: Không có cụm từ bị cấm
- **Mandatory Disclaimer**: Luôn hiển thị, không ẩn được
- **Read-Only**: Chỉ đọc & phân tích, KHÔNG thực hiện hành động
- **Data Masking**: Che số thẻ, số tài khoản
- **Audit Log**: Ghi nhận mọi cảnh báo

## ⚠️ Known Limitations

- Demo mode uses pre-computed outputs (cached data)
- Live mode requires valid BytePlus API key
- Statistical anomaly detection uses heuristic matching (production would need ML)
- Risk Score uses weighted formula (production would need training data)

---

> 🛡️ **Wealify Smart Finance** — AI Cross-Border Hackathon 2026  
> Powered by **BytePlus Seed 2.0**
