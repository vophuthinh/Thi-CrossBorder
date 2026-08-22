# 🛡️ Wealify Smart Finance
### AI-powered Dashboard for Expense Management & Transaction Safety — Cross-Border Sellers

> **WLF-01** — AI Cross-Border Hackathon 2026  
> Built with **BytePlus ModelArk (DeepSeek V4 Flash)** × **Wealify**

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

### Giao diện — chat làm trung tâm, không phải dashboard-tab

3 cột: **Command Center** (trái — các cờ cảnh báo: trùng lặp, khoản lạ, gói định kỳ/tăng giá, đối soát email, "Tạo report") · **Chat AI** (giữa — trả lời mọi câu hỏi bằng ngôn ngữ tự nhiên) · **Chi tiết** (phải — bấm 1 cờ ở Command Center để xem danh sách finding gốc, nhãn 3 mức + mốc hạn 60 ngày + nguồn). Có thêm trang riêng `/reminders` (cấu hình ngưỡng nhắc hạn) và `/setup` (setup wizard Gmail/Wealify/whitelist).

## 🏗️ Architecture

```
Input: Wealify API (live) + Gmail API (live) — không có dữ liệu giả cục bộ
      ↓
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│  Agent 1-2    │   Agent 3     │   Agent 4     │   Agent 7     │  finding_engine│
│  PARSE +      │   RECONCILE   │   ANOMALY     │   RISK        │  chuẩn hoá     │
│  MATCH EMAIL  │   3 nguồn     │   DETECT      │   SCORER      │  R-01→R-16     │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
      ↓
   Chat AI (trung tâm) + Command Center + Report Builder — 1 giao diện, HTML/CSS/JS
```

**Tech Stack:**
- **Backend**: Python + FastAPI (also serves the frontend, single process/port)
- **AI**: BytePlus ModelArk — DeepSeek V4 Flash (Responses API)
- **Frontend**: Chat-first workspace (HTML/CSS/JS), served by FastAPI at `/`
- **Safety**: Guardrails, trap detection, mandatory disclaimers
- **Design**: Trợ lý trò chuyện (chat AI làm trung tâm), không phải ô tìm kiếm/bảng lọc bấm chọn

> 📄 **Hướng dẫn cài đặt ngắn gọn (1-2 trang, chạy trong 10 phút):** [HUONG_DAN_CAI_DAT.md](HUONG_DAN_CAI_DAT.md)

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
> Phần đối chiếu email thật (đối soát email trong chat, các endpoint
> `/dashboard/*-reconciliation`, `/dashboard/suspicious-domains`) dùng Gmail API đọc
> + gửi hộp thư demo riêng của đội (`idm.hpt@gmail.com`, tạo riêng cho hackathon,
> không phải email cá nhân) — chìa khoá chỉ có 2 quyền `gmail.readonly` +
> `gmail.send` (không insert/modify/xoá), đúng nguyên tắc "chỉ đọc, chỉ gửi cho
> chính người dùng" của đề. Cần 2 file `gmail_credentials.json` và `gmail_token.json`,
> **đính kèm trong mục ghi chú riêng cho giám khảo của form nộp bài** (không commit
> vào repo public vì là thông tin xác thực). Giải nén và đặt cả 2 file vào `backend/`
> trước khi chạy `python main.py`.
> Thiếu 2 file này thì chat/finding chính vẫn chạy bình thường (dùng email mẫu cục bộ
> ở `backend/data/emails/` thay cho hộp thư thật), chỉ 3 endpoint đối chiếu email thật
> ở trên sẽ báo "unavailable".

### 3. Demo
1. Gõ vào khung chat: *"Tháng này tôi chi bao nhiêu, phí bao nhiêu, 3 khoản lớn nhất là gì?"*
2. Bấm cờ **"Trùng lặp giao dịch"** / **"Khoản lạ"** ở Command Center → xem danh sách finding chuẩn hoá (nhãn 3 mức, mốc hạn 60 ngày, nguồn)
3. Hỏi chat: *"Có tiền nào rời tài khoản mà chưa thấy lên thẻ không?"*
4. Bấm **"Tạo report"** → chọn tháng/quý/năm → xem biểu đồ + bấm gửi (phải xác nhận lần 2 mới gửi thật)
5. Thử câu gài (*"Tự huỷ mấy gói không dùng đi"*...) để xem guardrail từ chối khéo

## 📊 Demo Features

| Feature | Mô tả |
|---|---|
| Chat AI | Hỏi đáp tự nhiên, có/không LLM thật đều trả lời được (rule-based fallback) |
| Report Builder | Báo cáo tháng/quý/năm, biểu đồ Chart.js, gửi email có xác nhận 2 bước |
| 3-Source Reconciliation | Đối chiếu Account ↔ Card ↔ Wallet |
| Email Matching (2 chiều) | Tiền ra (biên lai thẻ) + Tiền vào (báo có VA) đối soát với Wealify thật |
| Subscription Tracking | Phát hiện gói quên huỷ (đánh dấu muốn huỷ >30 ngày vẫn active), tăng giá âm thầm |
| Amount Spike Detection | Giao dịch cao bất thường so với mức chi tiêu trung bình của chính tài khoản |
| Suspicious Domain Scan | Domain email giả mạo/lookalike so với whitelist |
| Song ngữ | Tiếng Việt / English |

## 🔑 Environment Variables

```env
BYTEPLUS_ENDPOINT=your_endpoint_id_here
BYTEPLUS_API_KEY=your_key_here
LLM_PROVIDER=byteplus    # byteplus | openai | anthropic
DEMO_MODE=true            # true = chat/insight rule-based (không gọi LLM); false = gọi LLM thật.
                          # KHÔNG ảnh hưởng dữ liệu Wealify/Gmail — 2 nguồn đó luôn live.

# Wealify — tài khoản mẫu BTC cấp, đã điền sẵn trong .env.example, không cần đổi.
WEALIFY_EMAIL=wealifytester@yopmail.com
WEALIFY_PASSWORD=Wealify@123
USE_LIVE_WEALIFY=true      # luôn true — không có fallback dữ liệu giả

# Gmail — đọc + gửi email thật, cần gmail_credentials.json + gmail_token.json
# (nhận riêng, xem lưu ý ở mục Quick Start). Chìa khoá chỉ 2 quyền: gmail.readonly
# + gmail.send. False thì chat/email dùng email mẫu cục bộ ở backend/data/emails/
# thay cho hộp thư thật — chỉ 3 endpoint *-reconciliation/suspicious-domains báo
# "unavailable" vì chúng luôn tự gọi Gmail API bất kể cờ này.
USE_GMAIL_API=false

# Self-notify: "gửi báo cáo vào email" chỉ gửi tới USER_EMAIL, không bao giờ gửi bên thứ 3.
USER_EMAIL=your_email@example.com
# Gửi qua Gmail API (dùng chung chìa khoá đọc mail ở trên) nếu USE_GMAIL_API=true.
# SMTP dưới đây chỉ là dự phòng khi chưa bật Gmail API. Nếu cả 2 đều thiếu, khi
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
│   │   ├── risk_scorer.py          # Agent 7: Risk Score
│   │   ├── email_classifier.py     # Lọc email quảng cáo khỏi luồng đối soát (LLM, có cache)
│   │   ├── inbound_reconciler.py   # Đối soát email báo có ↔ giao dịch VA thật (tiền vào)
│   │   └── outbound_reconciler.py  # Đối soát email biên lai ↔ giao dịch VC thật (tiền ra)
│   ├── finding_engine.py           # Sinh Finding chuẩn hoá theo rule R-01→R-16
│   ├── finding_schema.py           # Schema + nhãn 3 mức + fingerprint
│   ├── chat.py                     # Chat orchestrator
│   ├── llm_client.py               # BytePlus ModelArk (DeepSeek V4 Flash) wrapper
│   ├── safety.py                   # Guardrails & trap detection
│   ├── data_loader.py              # Đọc sao kê/ví/thẻ (live Wealify) + email (live Gmail hoặc mẫu cục bộ)
│   ├── wealify_client.py           # Live Wealify API client (chỉ đọc, che số ngay tại tầng gọi API)
│   ├── wealify_adapter.py          # Chuyển dữ liệu live Wealify sang schema nội bộ
│   ├── gmail_client.py             # Gmail API — đọc + gửi (gmail.readonly + gmail.send)
│   ├── email_sender.py             # Gửi self-notify (Gmail API, dự phòng SMTP)
│   ├── report_cache.py             # Job nền sinh sẵn báo cáo 12 tháng + năm
│   ├── reminder_checker.py         # Nhiệm vụ 7 — ngưỡng nhắc hạn cấu hình được
│   ├── domain_whitelist.py         # Danh sách domain email tin cậy (Setup Wizard)
│   ├── setup_api.py                # API cho Setup Wizard (/setup/*)
│   ├── audit_log.py                # Audit trail (chống báo trùng)
│   ├── config.py                   # Configuration
│   ├── trap_prompts.yaml           # 30 câu bẫy dùng để test guardrail
│   ├── test_traps.py               # Chạy 30 câu bẫy, kỳ vọng 30/30 bị từ chối
│   ├── test_chat_numbers.py        # Regression test số liệu chat so với ground truth tính trực tiếp
│   ├── evaluate.py                 # Chấm điểm findings so với ground_truth
│   └── requirements.txt
├── frontend-web/                   # Giao diện chính (HTML/CSS/JS), phục vụ qua FastAPI
│   ├── index.html                  # Trang chính: Command Center + Chat + Chi tiết + Report Builder
│   ├── app.js
│   ├── styles.css
│   ├── reminders.html              # Cấu hình ngưỡng nhắc hạn (Nhiệm vụ 7)
│   ├── setup.html / setup.js       # Setup Wizard (Gmail / Wealify / whitelist)
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
| GET | `/dashboard/reporting/meta` | Danh sách kỳ báo cáo có sẵn |
| GET | `/dashboard/reporting/month/{m}` \| `/quarter/{q}` \| `/year` | Báo cáo theo tháng/quý/năm (dùng cho "Tạo report") |
| POST | `/dashboard/reporting/send-email` | Gửi báo cáo — gọi lần 1 chỉ trả bản nháp (`status: "draft"`), phải gọi lại với `confirmed: true` mới gửi thật |
| GET | `/dashboard/wallet` | Số dư ví hiện tại |
| GET | `/dashboard/wealify-accounts` | VA/VC live từ Wealify API, chỉ đọc, đã che số |
| GET | `/dashboard/wealify-transactions` | Giao dịch thẻ live từ Wealify API |
| GET | `/dashboard/outbound-reconciliation` | Đối chiếu email biên lai thật ↔ giao dịch VC (cần Gmail) |
| GET | `/dashboard/inbound-reconciliation` | Đối chiếu email báo có VA ↔ giao dịch VA thật (cần Gmail) |
| GET | `/dashboard/reminders` | Nhiệm vụ 7 — khoản cần nhắc: email chưa xác nhận / giao dịch treo processing, theo ngưỡng ở `/reminders` |
| GET | `/dashboard/suspicious-domains` | Quét domain giả mạo/lookalike trong toàn bộ hộp thư (cần Gmail) |
| GET | `/setup` | Setup Wizard 3 bước (Gmail / Wealify / whitelist) |
| POST | `/ai/insight` | AI Insight (BytePlus ModelArk (DeepSeek V4 Flash)) |
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
- Wealify API `GET /v2/virtual-accounts/transactions` luôn trả `data: null` (lỗi phía Wealify, xác nhận qua nhiều lần thử) — nhưng `GET /v2/transactions/va` là endpoint **khác**, hoạt động bình thường và trả về đầy đủ giao dịch VA thật theo từng khoản (219 giao dịch thật ở thời điểm viết README này). App dùng endpoint này cho toàn bộ luồng "tiền vào": `/dashboard/inbound-reconciliation` đối chiếu email thật với giao dịch VA thật (không còn luôn báo "Chưa đủ dữ liệu"), báo cáo tháng/quý/năm tính "Tổng tiền vào" từ giao dịch nạp có ngày cụ thể thật (không phải suy diễn từ `total_received` — một trường tổng cộng trọn đời từng tài khoản, đã có bug ở bản trước dùng nhầm trường này gây sai hàng tỷ VND, đã sửa), và **R-09**/**R-11** trong `finding_engine.py` giờ chạy được trên dữ liệu live thật thay vì luôn im lặng. Số dư ví hiện tại (khớp trang Wealify) xem ở `/dashboard/wallet`.
- Statement thật trộn nhiều loại tiền (VND cho ví, USD/EUR cho thẻ) trên cùng tài khoản — mọi tổng số (summary, top3, theo tháng/quý/năm) đều tách riêng theo từng loại tiền, không quy đổi (Wealify API không có sẵn tỷ giá thật cho giao dịch thẻ, nên không tự bịa tỷ giá).
- Statistical anomaly detection uses heuristic matching (production would need ML)
- Risk Score uses weighted formula (production would need training data)

## 🧹 Sau khi thi

Toàn bộ dữ liệu mẫu và nhật ký được tạo/lưu trong lúc chạy demo. Sau khi giám khảo chấm xong, xoá:
- `backend/data/audit_log.json`, `backend/data/audit_log_export.json*` (nhật ký cảnh báo)
- `backend/out/` (findings/trap results xuất ra)
- `.env` (chứa API key / thông tin đăng nhập Wealify dev, không commit lên git)

---

> 🛡️ **Wealify Smart Finance** — AI Cross-Border Hackathon 2026  

