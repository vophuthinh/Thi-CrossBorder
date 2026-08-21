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

### Dashboard 5 Tab

| Tab | Nội dung |
|---|---|
| 📊 **Tổng quan** | Metric cards, charts thu/chi, phân bổ giao dịch, AI Insight |
| 🔍 **Đối chiếu** | 3-source reconciliation, email matching |
| 🛡️ **An toàn** | Risk gauge, gói đăng ký, tăng giá, khoản trùng |
| 🎯 **Findings** | Danh sách finding chuẩn hoá (nhãn 3 mức, mốc hạn 60 ngày, nguồn) |
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
   Dashboard (HTML/CSS/JS) + AI Insight (BytePlus Seed 2.0)
```

**Tech Stack:**
- **Backend**: Python + FastAPI (also serves the frontend, single process/port)
- **AI**: BytePlus Seed 2.0 (Omni — multi-modal LLM)
- **Frontend**: Static HTML/CSS/JS dashboard, served by FastAPI at `/`
- **Safety**: Guardrails, trap detection, mandatory disclaimers
- **Design**: Dashboard-first (không phải chatbot)

## 🚀 Quick Start (~2 phút)

### 1. Clone & Setup
```bash
git clone https://github.com/vophuthinh/Thi-CrossBorder.git
cd Thi-CrossBorder
```

### 2. Run
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# (Tuỳ chọn) sửa .env: thêm BYTEPLUS_API_KEY + BYTEPLUS_ENDPOINT để bật AI Insight/Chat qua LLM thật.
# Không có key vẫn chạy được — app tự dùng insight/chat rule-based có sẵn (DEMO_MODE=true).
python main.py
# → Mở http://localhost:8000 — dashboard + chat đều phục vụ tại đây, không cần chạy service nào khác.
```

### 3. Demo
1. Mở Dashboard → Tab **📊 Tổng quan** → xem metrics + charts
2. Tab **🔍 Đối chiếu** → xem khoản lệch giữa 3 nguồn
3. Tab **🛡️ An toàn** → xem Risk Score + gói đăng ký
4. Tab **🎯 Findings** → danh sách finding chuẩn hoá (PDF schema)
5. Tab **💬 Chat AI** → hỏi chi tiết (thử cả câu bẫy để xem guardrail từ chối)

> Ghi chú: thư mục `frontend/` (Streamlit) là bản dashboard cũ, không còn được `main.py` sử dụng — bản chính thức là `frontend-web/` (phục vụ trực tiếp qua FastAPI ở bước 2).

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

# Self-notify: "gửi báo cáo vào email" chỉ gửi tới USER_EMAIL, không bao giờ gửi bên thứ 3.
USER_EMAIL=your_email@example.com
# Cấu hình SMTP để gửi thật (vd Gmail + App Password). Nếu để trống, khi
# xác nhận "gửi" hệ thống sẽ hiển thị nội dung email để bạn tự gửi, thay vì
# giả vờ đã gửi.
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

## 📁 Project Structure

```
hackathon/
├── backend/
│   ├── main.py                     # FastAPI app — serves API + frontend-web at "/"
│   ├── agents/
│   │   ├── statement_parser.py     # Agent 1: Parse sao kê
│   │   ├── email_matcher.py        # Agent 2: Đối soát email
│   │   ├── reconciler.py           # Agent 3: Đối chiếu 3 nguồn
│   │   ├── anomaly_detector.py     # Agent 4: Phát hiện bất thường
│   │   ├── report_generator.py     # Agent 5: Báo cáo
│   │   ├── email_drafter.py        # Agent 6: Soạn email (chỉ nháp, không tự gửi)
│   │   └── risk_scorer.py          # Agent 7: Risk Score
│   ├── finding_engine.py           # Sinh Finding chuẩn hoá theo rule R-01→R-15
│   ├── finding_schema.py           # Schema + nhãn 3 mức + fingerprint
│   ├── chat.py                     # Chat orchestrator
│   ├── llm_client.py               # BytePlus Seed 2.0 wrapper
│   ├── safety.py                   # Guardrails & trap detection
│   ├── data_loader.py              # Data parsing + masking (mock CSV/JSON)
│   ├── wealify_client.py           # Live Wealify API client (optional, read-only)
│   ├── wealify_adapter.py          # Chuyển dữ liệu live Wealify sang schema nội bộ
│   ├── audit_log.py                # Audit trail (chống báo trùng)
│   ├── config.py                   # Configuration
│   ├── trap_prompts.yaml           # 30 câu bẫy dùng để test guardrail
│   ├── test_traps.py               # Chạy 30 câu bẫy, kỳ vọng 30/30 bị từ chối
│   ├── evaluate.py                 # Chấm điểm findings so với ground_truth
│   └── requirements.txt
├── frontend-web/                   # Dashboard chính thức (HTML/CSS/JS), phục vụ qua FastAPI
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── frontend/                       # (Cũ) bản Streamlit, không còn dùng trong main.py
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ API Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/health` | Health check + model info |
| GET | `/findings` | Findings chuẩn hoá (PDF schema) — dùng để chấm điểm bằng `evaluate.py` |
| GET | `/dashboard/overview` | Tổng quan tài chính |
| GET | `/dashboard/transactions` | Bảng giao dịch |
| GET | `/dashboard/anomalies` | Khoản bất thường, gói định kỳ, tăng giá |
| GET | `/dashboard/reconciliation` | Đối chiếu 3 nguồn |
| GET | `/dashboard/email-matches` | Đối soát email |
| GET | `/dashboard/risk-score` | Risk Score 0-100 |
| GET | `/dashboard/report` | Báo cáo tổng hợp |
| GET | `/dashboard/wallet` | Số dư ví hiện tại |
| GET | `/dashboard/wealify-accounts` | (Tuỳ chọn) VA/VC live từ Wealify API, chỉ đọc |
| GET | `/dashboard/wealify-transactions` | (Tuỳ chọn) Giao dịch thẻ live từ Wealify API |
| POST | `/ai/insight` | AI Insight (BytePlus Seed 2.0) |
| POST | `/chat` | Chat AI |
| POST | `/scheduled-check` | Chạy rà soát định kỳ, chống báo trùng |
| GET | `/audit-log` | Xem nhật ký cảnh báo |
| GET | `/audit-log/export` | Xuất nhật ký ra file JSON/JSONL |
| POST | `/reset` | Reset phiên demo (xoá dữ liệu/nhật ký) |

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

## 🧹 Sau khi thi

Toàn bộ dữ liệu mẫu và nhật ký được tạo/lưu trong lúc chạy demo. Sau khi giám khảo chấm xong, xoá:
- `backend/data/audit_log.json`, `backend/data/audit_log_export.json*` (nhật ký cảnh báo)
- `backend/out/` (findings/trap results xuất ra)
- `.env` (chứa API key / thông tin đăng nhập Wealify dev, không commit lên git)

---

> 🛡️ **Wealify Smart Finance** — AI Cross-Border Hackathon 2026  
> Powered by **BytePlus Seed 2.0**
