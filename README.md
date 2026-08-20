# 🔐 Wealify Smart Finance
### AI-powered Expense Management & Transaction Safety for Cross-Border Sellers

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

**AI Dashboard** phân tích toàn diện tài chính seller qua **3 AI Agents chuyên biệt**:

| Agent | Chức năng |
|---|---|
| 📊 **Expense Analyzer** | Phân tích chi tiêu, ROI per channel, gợi ý tiết kiệm |
| 🛡️ **Risk Detector** | Phát hiện giao dịch bất thường, risk scoring 0-100 |
| 💰 **Cashflow Forecaster** | Dự báo dòng tiền 7/14/30 ngày, runway, optimization |

## 🏗️ Architecture

```
Input: Dữ liệu giao dịch seller
      ↓
┌──────────────────┬──────────────────┬──────────────────┐
│  Agent 1          │   Agent 2         │   Agent 3         │
│  EXPENSE ANALYZER │   RISK DETECTOR   │   CASHFLOW        │
│  Chi tiêu + ROI   │   Fraud + Risk    │   FORECASTER      │
│  per channel      │   Scoring         │   Dự báo + tối ưu │
└──────────────────┴──────────────────┴──────────────────┘
      ↓
  Synthesis Dashboard + Alerts + Reports
```

**Tech Stack:**
- **Backend**: Python + FastAPI
- **AI**: BytePlus Seed 2.0 (Omni — multi-modal LLM)
- **Frontend**: Streamlit + Plotly
- **Design**: Dashboard-first (không phải chatbot)

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <repo-url>
cd hackathon
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Sửa .env: thêm BYTEPLUS_API_KEY
python main.py
# → API running at http://localhost:8000
```

### 3. Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
# → Dashboard at http://localhost:8501
```

### 4. Demo
1. Mở Dashboard → Sidebar chọn **Seller Profile**
2. Nhấn **🚀 Phân tích toàn diện**
3. Xem 3 tab: Chi tiêu / An toàn / Dòng tiền

## 📊 Demo Cases

| # | Seller | Scenario | Kết quả |
|---|---|---|---|
| 1 | GreenTote Shop (Etsy) | Healthy seller, ROI tốt | ✅ HEALTHY |
| 2 | TechGadget Pro (Amazon) | Có giao dịch fraud | 🚨 HIGH RISK |
| 3 | FashionVibe (Multi-platform) | Dòng tiền hụt | ⚠️ WARNING |

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
│   ├── main.py                     # FastAPI app
│   ├── agents/
│   │   ├── expense_analyzer.py     # Agent 1
│   │   ├── risk_detector.py        # Agent 2
│   │   └── cashflow_forecaster.py  # Agent 3
│   ├── llm_client.py               # BytePlus Seed 2.0 wrapper
│   ├── demo_data.py                # 3 seller profiles
│   ├── config.py                   # Configuration
│   └── requirements.txt
├── frontend/
│   ├── app.py                      # Streamlit Dashboard
│   └── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ API Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/health` | Health check + model info |
| GET | `/sellers` | List demo seller profiles |
| POST | `/analyze-expenses` | Agent 1: Phân tích chi tiêu |
| POST | `/detect-risks` | Agent 2: Phát hiện rủi ro |
| POST | `/forecast-cashflow` | Agent 3: Dự báo dòng tiền |
| POST | `/full-analysis` | **Full pipeline** (3 agents) |
| GET | `/usage` | LLM usage statistics |

## 🏆 Powered By

- **BytePlus Seed 2.0** — Core AI reasoning engine
- **Wealify** — Cross-border fintech domain expertise
- **FastAPI** — High-performance Python API
- **Streamlit + Plotly** — Interactive dashboard

## ⚠️ Known Limitations

- Demo mode uses pre-computed outputs (cached data)
- Live mode requires valid BytePlus API key
- Statistical anomaly detection uses simple z-score (production would need ML models)
- Cashflow projections assume stable patterns (no seasonal adjustment yet)

---

> 🔐 **Wealify Smart Finance** — AI Cross-Border Hackathon 2026  
> Powered by **BytePlus Seed 2.0**
