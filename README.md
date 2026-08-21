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

> **Dữ liệu là dữ liệu thật, không phải mock.** `.env.example` đã có sẵn tài khoản
> Wealify mẫu do BTC cấp (dùng chung cho mọi đội) nên không cần tự tạo tài khoản —
> app gọi thẳng Wealify API thật khi khởi động (`USE_LIVE_WEALIFY=true`, mặc định).
> Không có fallback sang dữ liệu giả: nếu Wealify API lỗi, app sẽ báo lỗi thay vì
> âm thầm hiện dữ liệu cũ.
>
> Phần đối chiếu email thật (tab đối chiếu, các endpoint `/dashboard/*-reconciliation`)
> dùng Gmail API đọc hộp thư demo riêng của đội (`idm.hpt@gmail.com`, tạo riêng cho
> hackathon, không phải email cá nhân) — cần 2 file `gmail_credentials.json` và
> `gmail_token.json`, **đính kèm trong mục ghi chú riêng cho giám khảo của form nộp
> bài** (không commit vào repo public vì là thông tin xác thực). Giải nén và đặt cả
> 2 file vào `backend/` trước khi chạy `python main.py`.
> Thiếu 2 file này thì phần chat/finding chính (dùng email mock đã tinh chỉnh) vẫn
> chạy bình thường, chỉ riêng 3 endpoint đối chiếu email thật sẽ báo lỗi.

### 3. Demo
1. Mở Dashboard → Tab **📊 Tổng quan** → xem metrics + charts
2. Tab **🔍 Đối chiếu** → xem khoản lệch giữa 3 nguồn
3. Tab **🛡️ An toàn** → xem Risk Score + gói đăng ký
4. Tab **🎯 Findings** → danh sách finding chuẩn hoá (PDF schema)
5. Tab **💬 Chat AI** → hỏi chi tiết (thử cả câu bẫy để xem guardrail từ chối)

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

# Wealify — tài khoản mẫu BTC cấp, đã điền sẵn trong .env.example, không cần đổi.
WEALIFY_EMAIL=wealifytester@yopmail.com
WEALIFY_PASSWORD=Wealify@123
USE_LIVE_WEALIFY=true      # luôn true — không có fallback dữ liệu giả

# Gmail — đối chiếu email thật, cần gmail_credentials.json + gmail_token.json
# (nhận riêng, xem lưu ý ở mục Quick Start). Cờ này KHÔNG ảnh hưởng /findings
# chính (luôn dùng email mock đã tinh chỉnh) — chỉ gate 3 endpoint đối chiếu
# email thật, các endpoint đó tự gọi Gmail API bất kể cờ này.
USE_GMAIL_API=false

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
| GET | `/dashboard/wealify-accounts` | VA/VC live từ Wealify API, chỉ đọc, đã che số |
| GET | `/dashboard/wealify-transactions` | Giao dịch thẻ live từ Wealify API |
| GET | `/dashboard/outbound-reconciliation` | Đối chiếu email biên lai thật ↔ giao dịch VC (cần Gmail) |
| GET | `/dashboard/inbound-reconciliation` | Đối chiếu email báo có VA ↔ giao dịch (cần Gmail; luôn "Chưa đủ dữ liệu" vì API VA-transactions của Wealify hiện lỗi) |
| GET | `/dashboard/suspicious-domains` | Quét domain giả mạo/lookalike trong toàn bộ hộp thư (cần Gmail) |
| GET | `/setup` | Setup Wizard 3 bước (Gmail / Wealify / whitelist) |
| POST | `/ai/insight` | AI Insight (BytePlus Seed 2.0) |
| POST | `/chat` | Chat AI |
| POST | `/scheduled-check` | Gọi tay 1 lần cơ chế rà soát định kỳ (xem mục dưới) |
| GET | `/audit-log` | Xem nhật ký cảnh báo |
| GET | `/audit-log/export` | Xuất nhật ký ra file JSON/JSONL |
| POST | `/reset` | Reset phiên demo (xoá dữ liệu/nhật ký) |

## 🛡️ Safety Features

- **Trap Question Detection**: Từ chối yêu cầu huỷ gói, gửi email bên thứ 3, kết luận an toàn
- **Response Validation**: Không có cụm từ bị cấm
- **Mandatory Disclaimer**: Luôn hiển thị, không ẩn được
- **Read-Only**: Chỉ đọc & phân tích, KHÔNG thực hiện hành động
- **Data Masking**: Che số thẻ, số tài khoản
- **Audit Log**: Ghi nhận mọi cảnh báo, không báo trùng khoản đã báo
- **Giám sát định kỳ tự động**: cứ mỗi `SCHEDULED_CHECK_INTERVAL_SECONDS` giây (mặc định 300s), server tự nạp lại dữ liệu live từ Wealify API và rà soát lại — chỉ ghi log khoản mới, **không tự gửi email** (self-notify vẫn cần xác nhận). Có thể gọi tay qua `POST /scheduled-check` để test ngay không cần chờ.

## ⚠️ Known Limitations

- `DEMO_MODE=true` chỉ tắt gọi LLM thật (dùng insight/chat rule-based) — dữ liệu tài chính (Wealify) và email luôn là dữ liệu thật, không có chế độ "cached/mock" cho phần này.
- Live mode requires valid BytePlus API key (AI Insight/Chat qua LLM thật)
- Wealify API `GET /v2/virtual-accounts/transactions` hiện luôn trả `data: null` (lỗi phía Wealify, không phải app) — vì vậy `/dashboard/inbound-reconciliation` luôn trả nhãn "Chưa đủ dữ liệu" thay vì đối chiếu được, đúng tinh thần không tự nhận đã kiểm tra khi chưa kiểm tra được.
- Cùng nguyên nhân trên: báo cáo tháng/quý/năm (`/dashboard/report`, tab Tổng quan, chat "tổng quan tài khoản") không tính được "Tổng tiền vào" theo từng khoản nạp có ngày cụ thể — vì API không cho danh sách giao dịch VA. App **không giả lập số này** (đã có bug ở bản trước lấy nhầm `total_received` — một trường tổng cộng trọn đời của mỗi tài khoản ảo — làm một giao dịch nạp trong ngày, khiến báo cáo hiện sai hàng tỷ VND; đã sửa, xác nhận khớp với số dư thật trên trang Wealify qua ảnh chụp màn hình). Số dư ví hiện tại (khớp trang Wealify) xem ở `/dashboard/wallet`; tổng nhận trọn đời từng tài khoản xem ở `/dashboard/wealify-accounts`.
- Statement thật trộn nhiều loại tiền (VND cho ví, USD/EUR cho thẻ) trên cùng tài khoản — mọi tổng số (summary, top3, theo tháng/quý/năm) đều tách riêng theo từng loại tiền, không quy đổi (Wealify API không có sẵn tỷ giá thật cho giao dịch thẻ, nên không tự bịa tỷ giá).
- Cùng nguyên nhân (API VA lỗi): 2 rule detector trong `finding_engine.py` không bao giờ báo trên dữ liệu live — **R-09** (nạp trùng, vì không có giao dịch nạp có ngày cụ thể để so trùng) và **R-11** (lệch số dư ví, vì không có dữ liệu số dư chạy theo từng giao dịch để tính số dư đầu kỳ thật). Đây là hành vi có chủ đích (thà im lặng còn hơn báo số bịa) chứ không phải bug — cả 2 vẫn hoạt động đầy đủ trên dữ liệu mock (`USE_LIVE_WEALIFY=false`).
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
