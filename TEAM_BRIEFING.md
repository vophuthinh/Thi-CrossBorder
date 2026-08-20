# 🤖 AI Cross-Border Hackathon 2026 — Báo cáo chuẩn bị team
> **v7 FINAL · Cập nhật: 20/08/2026 00:30**  
> Nguồn: Sổ tay thí sinh · 4 Webinar · aiglobal.dev · Luma · BytePlus Docs

**Nhãn đọc tài liệu:**
`[🏢 BTC]` = quy định chính thức từ BTC · `[🌐 WEB]` = thông tin website aiglobal.dev · `[💡 TEAM]` = chiến thuật team

---

## ⚠️ SOURCE OF TRUTH — Thông tin cần BTC xác nhận sáng 20/8

> Có xung đột giữa các nguồn. **Hỏi Ms. Yến Nhi (+84 905 780 862) sáng 20/8.**

| Thông tin | Webinar / Sổ tay | Website aiglobal.dev | Trạng thái | Ai xác nhận |
|---|---|---|---|---|
| **Deadline nộp bài** | **10:00** | **10:30** | ❓ Chưa chốt | Ms. Yến Nhi |
| **Số đội pitching** | **Top 8** | **Top 10** | ❓ Chưa chốt | Ms. Yến Nhi |
| **Thời lượng pitch** | 5–7 phút | Chưa ghi rõ | ❓ Chưa chốt | Mentor |
| **Pitching bắt đầu** | 14:50 | 14:45 | Tentative trên web | — |
| **Pre-implementation** | ≤ 30% | Chưa ghi rõ | ❓ Chưa chốt | Ms. Yến Nhi |
| **BytePlus sponsor bonus** | +5 điểm | +5 max (website) | ✅ Khớp | — |
| **Địa điểm** | The Zei, 8 Lê Đức Thọ | Luma: tầng 3, The Zei Plaza | ✅ Khớp | — |

> ⚡ **Tạm dùng deadline 10:00, Top 8** (thận trọng hơn).

### 10 câu PHẢI HỎI BTC sáng 20/8 hoặc 21/8

| # | Câu hỏi | Ai hỏi | Tại sao quan trọng |
|---|---|---|---|
| 1 | Deadline chính xác: **10:00 hay 10:30?** | Ms. Nhi | Quyết định lịch sprint |
| 2 | Top **8** hay **10** đội pitching? | Ms. Nhi | Ảnh hưởng khả năng vào vòng |
| 3 | Pitch bao nhiêu phút + Q&A bao nhiêu phút? | Mentor | Chuẩn bị script |
| 4 | +5 sponsor bonus cần điều kiện gì chính xác? | Ms. Nhi | Website không nói rõ cách lấy 5 điểm |
| 5 | Model chính **bắt buộc** BytePlus? Được fallback OpenAI/Claude không? | Mentor | Quyết định kiến trúc |
| 6 | Pre-built code ≤30% — tính thế nào? (LOC? Function? Module?) | Ms. Nhi | Tránh bị loại |
| 7 | Repo **private** hay **public**? | Ms. Nhi | GitHub settings |
| 8 | Nộp bài cần: **video demo / pitch deck** kèm? | Ms. Nhi | Chuẩn bị file |
| 9 | Scraping external APIs (được phép / cấm / hạn chế)? | Mentor | Ảnh hưởng PW1 data pipeline |
| 10 | Quyền IP: thuộc **team** hay **sponsor**? | Ms. Nhi | Post-hackathon plan |

---

## MỤC LỤC

0. [Source of Truth](#️-source-of-truth)
1. [Thông tin sự kiện](#1-thông-tin-sự-kiện)
2. [Giải thưởng](#2-giải-thưởng)
3. [Lịch thi](#3-lịch-thi)
4. [Tiêu chí chấm điểm](#4-tiêu-chí-chấm-điểm)
5. [Rubric 100 điểm + Score Matrix](#5-rubric-100-điểm)
6. [Công nghệ BytePlus được cấp](#6-công-nghệ-byteplus-được-cấp)
7. [Harness Engineering](#7-harness-engineering)
8. [6 đề bài chính thức](#8-6-đề-bài-chính-thức)
9. [Giải mã đề PW1](#9-giải-mã-đề-pw1)
10. [Giải mã đề PW2 Content Hub](#10-giải-mã-đề-content-hub)
11. [Phân tích chọn đề](#11-phân-tích-chọn-đề)
12. [Hiểu cuộc chơi](#12-hiểu-cuộc-chơi)
13. [Architecture & Tech Stack](#13-architecture)
14. [Code boilerplate](#14-code-boilerplate)
15. [Pitch & Evidence Pack](#15-pitch)
16. [Q&A Bank](#16-qa-bank)
17. [Sai lầm phổ biến](#17-sai-lầm-phổ-biến)
18. [Demo War Room](#18-demo-war-room)
19. [Nội quy & đồ mang theo](#19-nội-quy)
20. [Nộp bài & README Template](#20-nộp-bài)
21. [Kế hoạch 20/8 + Day 1](#21-kế-hoạch)
22. [Acceptance Tests](#22-acceptance-tests)
23. [Master Checklist](#23-master-checklist)
24. [Links & Liên hệ BTC](#24-links)

---

## 1. Thông tin sự kiện

| Hạng mục | Chi tiết |
|---|---|
| **Hackathon** | 21–22/8/2026 · Offline · 48h |
| **Summit chiều** | 22/8 · 13:00–18:00 · 400+ người |
| **Địa điểm** | 📍 **Forevermark Convention Center, The Zei** — 8 Lê Đức Thọ, Nam Từ Liêm, HN |
| **Di chuyển** | Từ nội thành ~30 phút · Grab 50k–80k VND |
| **Quy mô** | 300+ người · 15–20 đội thi |
| **Deadline nộp** | ⏰ **10:00 sáng 22/8** |
| **Pitching** | **Top 8** đội |

### Hệ sinh thái sponsor
```
┌─────────────────────────────────────────────────────────────┐
│                  CROSS-BORDER E-COMMERCE                     │
│                                                               │
│  [CONTENT]         [DATA]            [FULFILLMENT]           │
│  Ecomdy Media  →   Kalodata       →  Printway / BurgerPrints │
│  (TikTok Ads)      (Analytics)       (POD / Shipping)        │
│       ↑                ↑                    ↑                │
│       └────────────────┴────────────────────┘                │
│                        ↓                                      │
│             BytePlus (AI Infrastructure)                      │
│             Seed 2.0 · Seedream 5.0 · Seedance 2.0           │
│                        ↓                                      │
│             LianLian Global (Cross-border Payments)           │
└─────────────────────────────────────────────────────────────┘
```

| Vai trò | Đơn vị |
|---|---|
| Organizer | DNES + Ecomdy Media |
| Co-organizer | Printway · BurgerPrints |
| **Powered by ⭐** | **BytePlus** |
| Gold Sponsor | Kalodata |
| Bronze Sponsor | Wealify · USAdrop |
| Crowdfunding | PG Prints · GKE Logistics · Innovark · LianLian Global · Fristify · Trung Nguyên Legend |

---

## 2. Giải thưởng

| Hạng | Tiền |
|---|---|
| 🥇 1st | **10,000,000 VND** |
| 🥈 2nd | **7,000,000 VND** |
| 🥉 3rd | **5,000,000 VND** |
| ⭐ Best AI Tech | **2,000,000 VND** |
| 🚀 Potential Impact | **2,000,000 VND** |

**Ngoài tiền:** Giấy chứng nhận · Credit triển khai · Incubation · Launch sản phẩm quốc tế

---

## 3. Lịch thi

### Day 1 — 21/8
| Giờ | Hoạt động |
|---|---|
| 08:00 | Check-in (mang CCCD) |
| 08:30 | Khai mạc |
| 09:00 | **BẮT ĐẦU HACK** · Mentor |
| 10:00–11:00 | Training Session 1 |
| 11:00–12:00 | Lunch |
| 12:00–13:30 | Coffee Talk |
| 13:30–18:00 | Hack + Training 2 + Training 3 |
| **~18:00** | **Về nhà — tiếp tục code** |

### Day 2 — 22/8
| Giờ | Hoạt động |
|---|---|
| 08:00–10:00 | Sprint cuối |
| **10:00** | ⏰ **SUBMISSION DEADLINE** |
| 10:15–12:00 | Mentor chấm → chọn **Top 8** |
| 13:00 | Check-in chiều · Triển lãm |
| 13:30–14:50 | Khai mạc Summit + Speaker |
| 14:50–16:15 | **Top 8 Pitching** |
| 16:15–16:55 | Panel Discussion |
| **16:55–17:30** | 🏆 **Trao giải** |

---

## 4. Tiêu chí chấm điểm

### Hai hệ tiêu chí (cả hai đều đúng, dùng song song):

**Hệ A — 5 tiêu chí định tính (từ Webinar BTC):**

| # | Tiêu chí | Cách lấy điểm |
|---|---|---|
| 1 | Tính đổi mới & Sáng tạo | Multi-agent + dashboard, không clone tool có sẵn |
| 2 | Đột phá thực thi kỹ thuật | Seed 2.0 multi-modal, Harness Engineering |
| 3 | **⭐ Tác động kinh doanh thực tiễn** | ROI cụ thể, data thật, đúng pain point |
| 4 | Pitching & Trình bày | Live demo, storytelling, xử lý Q&A |
| 5 | Tiềm năng mở rộng | Roadmap, tích hợp hệ sinh thái sponsor |

> 🔥 **"Sản phẩm phải giải quyết nỗi đau thực tế của doanh nghiệp"** — BTC

### Insight:
```
❌ ĐỪNG xây Chatbot  ✅ HÃY xây Dashboard
Đề 1: Dashboard ĐIỂM SỐ + vòng đời  ·  Đề 2: CONTENT CALENDAR 5 nền tảng
```

---

## 5. Rubric 100 điểm + Score Maximization Matrix

> **Hệ B — Thang 100 điểm (từ website aiglobal.dev chính thức):**

| Tiêu chí | Điểm | Trọng số | Cách max điểm |
|---|---|---|---|
| **Solution Quality & Accuracy** | **30** | Cao nhất | Data thật, output đúng, explainable |
| **Usability & UX** | **20** | Cao | Dashboard ra quyết định < 30 giây |
| **Technical Execution** | **20** | Cao | Seed 2.0 + data pipeline, code chạy thật |
| **Innovation & Differentiation** | **15** | TB | Góc mới, không copy ChatGPT wrapper |
| **Demo, Docs & Presentation** | **15** | TB | Live demo + README đầy đủ |
| **Sponsor Bonus (max)** | **+5** | Bonus | Xác nhận điều kiện chính xác với BTC |
| **TỔNG** | **100 + 5** | | |

### Score Maximization Matrix — Ví dụ PW1

| Rubric (điểm) | Chiến thuật cụ thể cho PW1 |
|---|---|
| **Accuracy 30** | Chứng minh scoring đúng: test 5 SP đã biết kết quả, so sánh AI vs thực tế |
| **UX 20** | Dashboard hiển thị 9 chỉ số + verdict trong < 30s, 1 click export PDF |
| **Technical 20** | Seed 2.0 Omni + 3-agent pipeline + data normalization |
| **Innovation 15** | Lifecycle stage detection + confidence score + "Why this score?" |
| **Demo/Docs 15** | Live scenario 3 SP + README quick start + known limitations |
| **Sponsor +5** | Multi-agent reasoning rõ ràng với BytePlus, ghi "Powered by" trên UI |

---

## 6. Công nghệ BytePlus được cấp

> ✅ **BTC CUNG CẤP các API/model sau cho đội thi:**

| Model | Loại | Khả năng | Dùng cho |
|---|---|---|---|
| **Seed 2.0** (Omni) | LLM lõi | Xử lý đồng thời Video + Image + Audio + Text · **Hỗ trợ tiếng Việt tốt** · Trích xuất info từ video dài (tìm hook, key selling point từ giây X đến giây Y) | Core reasoning, agent pipeline |
| **Seedream 5.0 Lite** | Image Generation | Sinh ảnh từ text · Dùng trong R&D để vẽ Storyboard cho video quảng cáo | Product mockup, storyboard |
| **Seedance 2.0** (SOTA) | Video Generation | Input: text, ảnh, video tham chiếu, audio · Output: tối đa **1080p**, **4–15 giây** · Giữ nguyên character identity, màu sắc thương hiệu, chuyển động vật lý chính xác | TikTok video ads, demo clips |

### BytePlus Endpoint (hackathon)
```
Endpoint: your_endpoint_id_here
Base URL: https://ark.ap-southeast.bytepluses.com/api/v3
API Key:  [nhận từ BTC tại khai mạc 21/8 hoặc hỏi trước]
```

### ⚠️ API Key — hành động cụ thể
- **Sáng 21/8**: Chủ động hỏi **Mentor BytePlus** ngay khi check-in nếu chưa nhận key
- **Nếu key chưa có**: Dùng Playground trên console.byteplus.com để test trước
- **Plan B**: Chuẩn bị sẵn **GPT-4o** hoặc **Claude** key cá nhân — code wrapper phải hỗ trợ switch provider chỉ bằng đổi env var

### ⚠️ Thông tin cần xác nhận lại với BTC
| Thông tin | Ghi trong tài liệu | Cần confirm |
|---|---|---|
| Deadline nộp bài | **10:00** | Double-check Sổ tay thí sinh lần cuối |
| Số đội pitching | **Top 8** | Một số nguồn cũ ghi Top 10 — hỏi BTC |
| API key cách nhận | Nhận tại khai mạc | Hỏi BTC có nhận trước được không |

> 💡 **Seed 2.0 Omni = vũ khí chính.** Nó không chỉ là text LLM — nó xử lý VIDEO + IMAGE + AUDIO cùng lúc. Tận dụng multi-modal để differentiate.

---

## 7. Harness Engineering (Phương pháp luận từ Webinar)

> *Thay vì Prompt Engineering hay Context Engineering đơn thuần → xây "Meta Harness System"*

### File Execution Book — 5 bước AI tự sửa code:
```
1. Research   → AI đọc và tìm giải pháp
2. Plan Spec  → Viết kế hoạch và review
3. Code       → Chạy code thực tế
4. Fixing     → Xử lý bugs nếu kẹt
5. Test/Link  → Cập nhật docs để AI "nhớ" cho lần sau
```

### Nguyên tắc "Window Zero-sum":
```
❌ Đừng nhồi quá nhiều instruction vào 1 AI
❌ Đừng tạo Persona quá phức tạp → hiệu năng tệ
✅ Chia nhỏ Agent, mỗi Sub-agent giải quyết ĐÚNG 1 VIỆC
✅ 1 Input → 1 Output rõ ràng (VD: Agent chỉ chuyên đọc CSV)
```

### Gợi ý kỹ thuật:
- Dùng **Cline** (đang top 1 GitHub) + giao thức **MCP** để quản lý skills cho AI
- Multi-agent workflows: agent chuyên biệt → output sắc nét hơn 1 agent "biết tuốt"

---

## 8. 6 đề bài chính thức

> 📋 Chi tiết tại: https://byvn.net/lO63

| Mã đề | Tên bài toán | Nhà tài trợ | Ghi chú |
|---|---|---|---|
| **PW1** | Product Opportunity Hub | Printway | 9 chỉ số chấm điểm bắt buộc |
| **PW2** | AI Content Hub | Printway | Content Calendar đa kênh + Brand Voice |
| **BUP-01** | AI Ads Video Generator | BurgerPrints | Seedance 2.0 |
| **BUP-02** | AI Design Compliance Checker | BurgerPrints | |
| **BP-01** | Commerce Campaign Launch Copilot | BytePlus | Multi-agent workflow |
| **BP-02** | AI iTVC Campaign Studio | BytePlus | Video campaign end-to-end |

---

## 9. Giải mã đề PW1 — Product Opportunity Hub

> *Nguồn: Video 3 — Printway Sharing 1*

### Bài toán thực tế:
Team R&D ngành Print on Demand (POD) đang:
- Mất rất nhiều thời gian **thu thập dữ liệu thủ công** từ mạng xã hội/sàn TMĐT
- Khó **đồng nhất tên sản phẩm** giữa các nguồn khác nhau
- Thiếu công cụ **tổng hợp đánh giá vòng đời sản phẩm**

### Yêu cầu output:
AI Tool tổng hợp dữ liệu đa nguồn, ghép nối listing với catalog sản phẩm → **tự động chấm điểm** → kết luận "CÓ NÊN SẢN XUẤT/BÁN HAY KHÔNG"

### ⭐ 9 chỉ số chấm điểm — BẮT BUỘC PHẢI CÓ:

#### Nhóm 1: Khả năng sản xuất (Production)
| # | Chỉ số | Ý nghĩa |
|---|---|---|
| 1 | **Production Fit** | Năng lực máy móc/vật liệu có làm được không? Tỉ lệ lỗi dự kiến? |
| 2 | **Production Time** | Tổng thời gian từ nhận đơn → tay khách |
| 3 | **Seasonality** | Có kịp cho dịp lễ (Halloween, Christmas) không? |
| 4 | **Personalization** | Có cá nhân hóa được không? (in tên, đổi ảnh, khắc chữ) |

#### Nhóm 2: Hiệu quả tài chính
| # | Chỉ số | Ý nghĩa |
|---|---|---|
| 5 | **Doanh thu tiềm năng** | Lịch sử doanh thu niche này năm ngoái |
| 6 | **Biên lợi nhuận** | Sau trừ giá vốn, ship, chi phí → lãi bao nhiêu? |

#### Nhóm 3: Thị trường
| # | Chỉ số | Ý nghĩa |
|---|---|---|
| 7 | **Nhu cầu thị trường** | Lượt tìm kiếm, lượt bán, lượt yêu thích |
| 8 | **Tốc độ tăng trưởng** | Đang lên hay đang giảm? (doanh thu to nhưng giảm → KHÔNG làm) |
| 9 | **Mức độ cạnh tranh** | Số đối thủ mới, số mẫu thiết kế trùng lặp |

### Vòng đời sản phẩm (phải hiển thị trên Dashboard):
```
Hình thành → Ra mắt → Tăng trưởng → Bão hòa → Suy thoái
(Conception)  (Launch)   (Growth)    (Saturation)  (Decline)
```

### PW1 Scoring Specification — Công thức chấm điểm

> GK sẽ hỏi: "78/100 từ đâu ra?" — phải trả lời được.

**Pipeline:** Raw Data → Normalize (0–10) → Weight → Confidence → Score

| Chỉ số | Trọng số | Lý do | Data source |
|---|---|---|---|
| Production Fit | 10% | Quan trọng nhưng ít biến động | KB nội bộ Printway |
| Production Time | 10% | Ảnh hưởng trực tiếp đến fulfillment | Hard-code theo loại SP |
| Seasonality | 10% | Quyết định timing launch | Google Trends + lịch lễ |
| Personalization | 5% | Nice-to-have, không bắt buộc | Catalog Printway |
| Revenue Potential | 15% | Trọng số cao — quyết định ROI | Kalodata / Etsy search volume |
| Profit Margin | 15% | Trọng số cao — quyết định ROI | Hard-code COGS + shipping |
| Market Demand | 15% | Signal chính | Kalodata trending / search vol |
| Growth Rate | 10% | Xu hướng > số tuyệt đối | So sánh MoM / YoY |
| Competition | 10% | Ít cạnh tranh = cơ hội | Đếm listing trên Etsy/Amazon |
| **TỔNG** | **100%** | | |

**Dashboard phải có:** `[💡 TEAM]`
- "Why this score?" — giải thích từng chỉ số
- "Data confidence: High / Medium / Low" — minh bạch data quality
- Verdict: NÊN / KHÔNG NÊN / CẦN THÊM DATA

### Ground Truth & Data Provenance

> Mỗi datapoint trong scoring pipeline phải lưu:

```json
{
  "metric": "market_demand",
  "value": 8.5,
  "source": "kalodata_api",
  "collected_at": "2026-08-21T10:30:00Z",
  "data_type": "cached",      // "live" | "cached" | "manual" | "demo"
  "confidence": "high",        // "high" | "medium" | "low"
  "note": "Kalodata trending top 50, Aug 2026"
}
```

> GK hỏi "78/100 từ đâu?" → dashboard mở **evidence chain**, không chỉ explanation của LLM.

### Data Source & Fallback Matrix

| Nguồn data | Primary (live) | Fallback 1 (cached) | Fallback 2 (upload) | Demo fallback |
|---|---|---|---|---|
| **Kalodata** | API nếu BTC cấp | Cached JSON 20 SP | CSV upload | Hard-code 5 SP |
| **Etsy** | Web scraping | Cached HTML | User paste URL | Pre-scraped data |
| **Amazon** | Product API | Cached response | User paste ASIN | Hard-code |
| **Google Trends** | PyTrends API | Cached CSV | Manual input | Hard-code trend |
| **Printway catalog** | Nếu có API | KB JSON file | User upload | Hard-code |

> ⚠️ **ĐỪNG để live demo phụ thuộc 3 website ngoài cùng lúc.** Luôn có cached data.

### Output lý tưởng = Dashboard:
```
┌──────────────────────────────────────────────┐
│  PRODUCT OPPORTUNITY DASHBOARD               │
│  Sản phẩm: [Áo thun Graphic Halloween]       │
│  Vòng đời: ████████░░ Tăng trưởng (Growth)   │
│  Data Confidence: ██████████ High             │
│                                               │
│  ┌─────────────────────────────────────────┐  │
│  │ ĐIỂM SỐ TỔNG: 78/100 → KHUYẾN NGHỊ ✅  │  │
│  └─────────────────────────────────────────┘  │
│                                               │
│  Production Fit    ██████████ 9/10  ℹ️ Why?   │
│  Market Demand     █████████░ 9/10  ℹ️ Why?   │
│  Revenue Potential ████████░░ 8/10  ℹ️ Why?   │
│  ...                                          │
│                                               │
│  → KẾT LUẬN: NÊN SẢN XUẤT. Kịp Halloween.   │
│  → [Xuất PDF] [Xem chi tiết] [So sánh SP]    │
└──────────────────────────────────────────────┘
```

---

## 10. Giải mã đề Content Hub (PW2)

> *Nguồn: Video 4 — Printway Sharing 2*

### Bài toán:
Team Content phải quản trị nội dung **đa kênh** (Facebook, TikTok, YouTube, Instagram, Email) cho **nhiều thị trường** (VN, Global). Khối lượng thủ công khổng lồ.

### Yêu cầu: AI Content Hub — "Trợ lý Giám đốc Nội dung"
Người dùng nhập 1 brief (VD: "Ra mắt bộ sưu tập Halloween") → AI tự động phân bổ:

### 6 Content Angle (góc khai thác) — AI phải tự chẻ ra:
| Angle | Ý nghĩa | Ví dụ |
|---|---|---|
| **Product** | Tính năng, chất liệu | "5 chất liệu cotton cao cấp cho mùa hè" |
| **Collection** | Gợi ý theo bộ, theo mùa | "Top 10 designs cho Halloween 2026" |
| **Branding** | Kể chuyện nhà máy, năng lực | "Bên trong dây chuyền in ấn Printway" |
| **Event** | Webinar, sự kiện | "Printway x Ecomdy: Live Selling Workshop" |
| **Education** | Bí kíp thiết kế, hướng dẫn | "Cách tối ưu file PNG cho in POD" |
| **Insight** | Phân tích trend, nhu cầu | "3 xu hướng thiết kế đang tăng Q3/2026" |

### Platform Formats — AI phải tùy biến theo từng kênh:
| Kênh | Format yêu cầu |
|---|---|
| **TikTok** | Hook 3 giây → Insight thị trường → Demo sản phẩm → CTA · Video dọc 15–60s |
| **Facebook** | Caption dài, chi tiết USP/giá/kích thước, hình ảnh rõ ràng |
| **YouTube** | Video dài chuyên sâu, case study, webinar hoặc Shorts |
| **Instagram** | Visual-first, carousels, story |
| **Email** | Tiêu đề giật gân, nội dung nuôi dưỡng, remarketing |

### Brand Voice Printway — 5 đặc điểm (BẮT BUỘC tuân thủ):
```
1. Mang lại giá trị  → Không viết sáo rỗng
2. Chuyên nghiệp     → Rõ ràng, có căn cứ
3. Đáng tin cậy      → KHÔNG phóng đại, KHÔNG bịa số liệu, KHÔNG hứa hẹn viển vông
                       ⚠️ Đây là lỗi Hallucination AI hay gặp → CẦN GUARDRAIL
4. Gần gũi           → Đứng từ góc nhìn Seller để khuyên bảo
5. Truyền cảm hứng   → Khuyến khích Seller thử nghiệm
```

### Output lý tưởng = Content Calendar Dashboard:
```
┌──────────────────────────────────────────────────────────┐
│  CONTENT CALENDAR — Tuần 34/2026                         │
│  Brief: "Ra mắt bộ sưu tập Halloween"                   │
│                                                           │
│  Thứ │ TikTok        │ Facebook      │ Email             │
│  ────┼───────────────┼───────────────┼──────────────────  │
│  T2  │ Hook video    │ Product post  │ Teaser email       │
│      │ "3 designs    │ "5 mẫu áo    │ "Halloween is      │
│      │  hot nhất"    │  Halloween"   │  coming 🎃"        │
│  T4  │ Behind scene  │ Collection    │ —                  │
│      │ Branding      │ showcase      │                    │
│  T6  │ Trend insight │ Education:    │ Launch email       │
│      │ video         │ "Cách chọn    │ "Mở bán chính     │
│      │               │  design POD"  │  thức"             │
│                                                           │
│  [Xem chi tiết] [Xuất Notion] [Xuất PDF]                 │
└──────────────────────────────────────────────────────────┘
```

---

## 11. So sánh 6 đề bài — Bảng quyết định

> **Chốt tối nay** — TEAM_BRIEFING này là cơ sở để bàn.

| Đề bài | Nhà tài trợ | Bản chất giải pháp | Độ khó KT | WOW Demo | Kiểm soát 48h | Tác động kinh doanh | Phù hợp đội nào | Khuyến nghị |
|--------|-------------|--------------------|-----------|----------|---------------|---------------------|-----------------|--------------|
| **PW1** Product Opportunity Hub | Printway (Co-org) | Dashboard chấm điểm SP theo 9 chỉ số + vòng đời | TB | Cao (Dashboard + Scoring) | Cao | Rất cao (đúng pain R&D POD) | Đội mạnh data + logic + UI | **Nên chọn** nếu muốn scope rõ |
| **PW2** AI Content Hub | Printway (Co-org) | Content Calendar đa kênh từ 1 brief + Brand Voice | TB | Cao (Calendar đẹp) | Cao | Cao (giải bài toán content đa kênh) | Đội mạnh content + prompt + design | **Nên chọn** nếu mạnh content |
| **BP-01** Campaign Launch Copilot | BytePlus (Powered by) | Multi-agent lập kế hoạch campaign hoàn chỉnh | TB – Thấp | TB | **Cao nhất** | Cao | Đội mạnh LLM Agent + workflow + UI | **An toàn nhất** |
| **BUP-01** AI Ads Video Generator | BurgerPrints (Co-org) | Tự động tạo video ads TikTok từ sản phẩm | Cao | **Rất cao** (video live) | TB – Thấp | Cao | Đội có kinh nghiệm video gen / Seedance | Chỉ chọn khi chắc video |
| **BP-02** AI iTVC Campaign Studio | BytePlus | Studio tạo video campaign end-to-end | Cao | Cao | TB | Cao | Đội mạnh multimodal + video | Rủi ro cao hơn BP-01 |
| **BUP-02** AI Design Compliance Checker | BurgerPrints | Kiểm tra design tuân thủ quy định | Thấp – TB | Thấp | Cao | TB – Thấp | Đội muốn làm đơn giản | **Không khuyến nghị** |

### Tóm tắt nhanh quyết định

| Mục tiêu của đội | Đề nên chọn |
|---|---|
| Muốn **an toàn + điểm ổn định** | **BP-01** |
| Muốn **scope rõ ràng + đúng pain Printway** | **PW1** |
| Muốn **content + multi-channel** | **PW2** |
| Muốn **WOW tối đa bằng video** và đã có kinh nghiệm | **BUP-01** |

**Quy tắc vàng:** Chọn đề mà đội **làm tốt nhất trong 48 giờ** — không chọn vì "nghe hay" hay "ít người chọn".

### Rủi ro cụ thể từng đề + cách giảm thiểu

| Đề | Rủi ro chính | Cách giảm thiểu |
|---|---|---|
| **PW1** | Data scraping từ Etsy/Amazon bị block | Hard-code 20–30 sample products sẵn, dùng mock data có cấu trúc thật |
| **PW2** | Content AI sinh ra sai Brand Voice / hallucinate số liệu | Guardrail prompt chặt + 5 đặc điểm Brand Voice trong system prompt |
| **BP-01** | Output quá generic, không actionable | Chuẩn bị real case data, ép output JSON có cấu trúc, có "Vì sao" cho mỗi gợi ý |
| **BUP-01** | Video kém chất lượng (méo, text lỗi) đúng lúc demo | Pre-generate 5–10 video đẹp sẵn + 1 người QC video + fallback Kling/Runway |
| **BP-02** | Video campaign end-to-end quá phức tạp cho 48h | Cắt scope: chỉ làm 1 flow (brief → script → 1 video), không làm full campaign |

### Q&A khó dự đoán — luyện trước cho từng đề

| Đề | Câu hỏi khó | Gợi ý trả lời |
|---|---|---|
| **PW1** | "9 chỉ số lấy data từ đâu?" | "Kết hợp Kalodata API (trending) + web scraping Etsy/Amazon + knowledge base ngành POD" |
| **PW1** | "Accuracy chấm điểm bao nhiêu?" | "Test với X sản phẩm Printway đã biết kết quả → Y% trùng khớp" |
| **PW2** | "AI làm sao giữ Brand Voice nhất quán?" | "System prompt encode 5 đặc điểm + Guardrail kiểm tra output trước khi hiển thị" |
| **BP-01** | "Khác ChatGPT chỗ nào?" | "ChatGPT không có data thị trường specific + không có multi-agent reasoning chuyên biệt" |
| **BUP-01** | "Video chỉ 5 giây, seller dùng thế nào?" | "Dùng làm hook clip → ghép vào video dài hơn, hoặc dùng trực tiếp cho TikTok ads" |

---

## 12. Hiểu cuộc chơi

### Ai chấm điểm bạn?

> Đây là **business pitch có technical demo**, KHÔNG phải thi lập trình.

| Người chấm | Background | Họ muốn thấy gì |
|---|---|---|
| **Ecomdy** | TikTok Agency | Giải pháp giúp khách hàng kiếm tiền |
| **BytePlus** | Cloud AI (ByteDance) | Sản phẩm của họ được dùng thông minh |
| **DNES** | Startup incubator | Dự án thành startup thực được |
| **Printway** | POD fulfillment | Bài toán logistics/R&D cross-border |
| **Kalodata** | TikTok analytics | Data-driven decisions |

**→ Quy tắc vàng:** Giải quyết đúng bài toán của đúng người > code phức tạp nhất.

### Benchmark: Đội thắng Đà Nẵng (ViralScore)
| Yếu tố | Cách làm |
|---|---|
| Bài toán | Cực cụ thể, đo lường được |
| User | 1 target duy nhất |
| Tech | Multi-modal nhưng không over-engineer |
| Demo | Live với data thật, không mock |

---

## 13. Architecture

### Nguyên tắc chung (áp dụng cho mọi đề):
```
✅ Dashboard > Chatbot
✅ 3 agent sâu > 5 agent dang dở
✅ Mỗi sub-agent giải quyết ĐÚNG 1 VIỆC (Window Zero-sum)
✅ Dùng Seed 2.0 Omni (multi-modal) để differentiate
```

### PW1 Architecture:
```
Input: URL sản phẩm / keyword / hình ảnh
      ↓
┌──────────────┬───────────────┬────────────────┐
│  Agent 1     │   Agent 2     │   Agent 3      │
│  DATA SCRAPER│   SCORER      │   LIFECYCLE    │
│  Thu thập từ │   Chấm 9 chỉ │   Xác định     │
│  Etsy/Amazon │   số sản phẩm │   giai đoạn    │
│  /TikTok     │               │   vòng đời     │
└──────────────┴───────────────┴────────────────┘
      ↓
Synthesis → Verdict: "NÊN/KHÔNG NÊN sản xuất"
      ↓
Dashboard + Xuất báo cáo PDF
```

### BP-01 Architecture:
```
Input: Brief (tên SP, mục tiêu, budget, market, thời gian)
      ↓
┌──────────────┬───────────────┬────────────────┐
│  Agent 1     │   Agent 2     │   Agent 3      │
│  RESEARCH    │   STRATEGY    │   CREATIVE     │
│  product +   │   audience +  │   ad copy +    │
│  market      │   channel mix │   visual ideas │
└──────────────┴───────────────┴────────────────┘
      ↓
Campaign Plan Dashboard + Export
```

### Tech Stack:
```
Backend:    Python + FastAPI
LLM:        BytePlus Seed 2.0 (Omni — multi-modal)
Image:      BytePlus Seedream 5.0 Lite
Video:      BytePlus Seedance 2.0 (nếu chọn BUP-01)
Frontend:   Streamlit (nhanh nhất) hoặc Next.js
Deploy:     Vercel (FE) + Railway (BE)
```

### Project structure:
```
hackathon/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── agents/
│   │   ├── research.py      # Agent 1
│   │   ├── scorer.py        # Agent 2 (hoặc strategy.py)
│   │   └── creative.py      # Agent 3 (hoặc lifecycle.py)
│   ├── llm_client.py        # BytePlus Seed 2.0 wrapper
│   └── requirements.txt
├── frontend/
│   └── app.py               # Streamlit Dashboard
├── .env.example
├── .gitignore
└── README.md
```

---

## 14. Code boilerplate

### BytePlus Seed 2.0 — LLM client (dùng HTTP thuần, không cần SDK)

```python
# llm_client.py
import os, json, urllib.request

ENDPOINT = os.getenv("BYTEPLUS_ENDPOINT", "your_endpoint_id_here")
API_KEY = os.getenv("BYTEPLUS_API_KEY", "")
BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions"

def call_llm(prompt: str, system: str = "You are a helpful assistant.", max_tokens: int = 800) -> str:
    payload = {
        "model": ENDPOINT,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    req = urllib.request.Request(
        BASE_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read())
        return result["choices"][0]["message"]["content"]
```

### FastAPI Backend mẫu (BP-01)

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_client import call_llm

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

class CampaignRequest(BaseModel):
    product_name: str
    product_desc: str
    goal: str        # "awareness" | "conversion" | "traffic"
    budget: float
    market: str      # "US", "SEA", "EU"
    duration: str

@app.post("/generate-campaign")
async def generate_campaign(req: CampaignRequest):
    research = call_llm(
        f"Phân tích '{req.product_name}' cho thị trường {req.market}. "
        f"Trả về JSON: target_demographics, market_trends, competitors",
        system="You are a market research analyst for cross-border e-commerce."
    )
    strategy = call_llm(
        f"Dựa trên: {research}\nTạo strategy: {req.goal}, ${req.budget}, {req.duration}. "
        f"Trả về JSON: audience_segments, channel_mix, budget_allocation",
        system="You are a cross-border campaign strategist."
    )
    creative = call_llm(
        f"Dựa trên: {strategy}\nTạo ad creatives cho {req.product_name} tại {req.market}. "
        f"Trả về JSON: ad_copies, visual_ideas, hashtags, hooks",
        system="You are a creative director for TikTok and social ads."
    )
    return {"research": research, "strategy": strategy, "creative": creative,
            "powered_by": "BytePlus Seed 2.0"}

@app.get("/health")
def health():
    return {"status": "ok", "powered_by": "BytePlus Seed 2.0"}
```

### Seedream 5.0 — Image Generation

```python
# image_gen.py
import requests, os

# Dùng Endpoint ID thực tế từ BTC thay vì generic model name
SEEDREAM_ENDPOINT = os.getenv("BYTEPLUS_SEEDREAM_ENDPOINT", "seedream-5.0-lite")

def generate_image(prompt: str) -> str:
    response = requests.post(
        "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations",
        json={"model": SEEDREAM_ENDPOINT, "prompt": prompt, "size": "1024x1024"},
        headers={"Authorization": f"Bearer {os.getenv('BYTEPLUS_API_KEY')}",
                 "Content-Type": "application/json"}
    )
    return response.json().get("data", [{}])[0].get("url")
```

### Seedance 2.0 — Video Generation (⚠️ Async Task API)

> **LƯU Ý:** BytePlus dùng **asynchronous task API**, KHÔNG trả video_url đồng bộ.  
> Model ID: `dreamina-seedance-2-0-260128` (từ docs BytePlus).
> Video URL có hiệu lực **24 giờ** — phải tải/cache lại.

```python
# video_gen.py — ASYNC API (đúng theo BytePlus Docs)
import requests, os, time

BASE = "https://ark.ap-southeast.bytepluses.com/api/v3"
KEY = os.getenv("BYTEPLUS_API_KEY", "")
SEEDANCE_MODEL = os.getenv("BYTEPLUS_SEEDANCE_ENDPOINT", "dreamina-seedance-2-0-260128")
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

def generate_video(prompt: str, duration: int = 5, aspect: str = "9:16") -> str:
    """Submit task → poll until done → return video URL. Cache video locally!"""
    # Step 1: Submit task
    resp = requests.post(
        f"{BASE}/contents/generations/tasks",
        json={"model": SEEDANCE_MODEL, "content": {"prompt": prompt},
              "duration": duration, "aspect_ratio": aspect},
        headers=HEADERS, timeout=30
    )
    resp.raise_for_status()
    task_id = resp.json()["data"]["task_id"]
    print(f"[Seedance] Task submitted: {task_id}")

    # Step 2: Poll for result (max 5 min)
    for _ in range(60):
        time.sleep(5)
        poll = requests.get(
            f"{BASE}/contents/generations/tasks/{task_id}",
            headers=HEADERS, timeout=15
        )
        data = poll.json().get("data", {})
        status = data.get("status")
        if status == "succeeded":
            video_url = data["output"]["video_url"]
            print(f"[Seedance] Done: {video_url}")
            # ⚠️ URL expires in 24h — download & cache locally!
            return video_url
        elif status == "failed":
            raise RuntimeError(f"Seedance failed: {data.get('error')}")
        print(f"[Seedance] Polling... status={status}")

    raise TimeoutError("Seedance task timed out after 5 minutes")
```

---

## 15. Pitch & Evidence Pack

### Tâm lý giám khảo
15–20 bài pitch trong 1 ngày → sau bài thứ 5 họ mệt.
- Bắt đầu bằng **con số gây shock**
- **1 moment "wow"** trong demo (chỉ cần 1)
- Kết thúc bằng **vision rõ ràng**

### Kịch bản 7 phút:
```
⏱ 0:00–0:30 — HOOK (đừng giới thiệu tên team)
"Mỗi tuần, đội R&D ngành POD dành [X] giờ phân tích thủ công.
[Y]% sản phẩm mới fail vì thiếu data. Đó là tiền và thời gian đốt."

⏱ 0:30–1:30 — PROBLEM (1 nhân vật)
"Chị Hương — leader team R&D. Mỗi tuần phải đánh giá
20 ý tưởng sản phẩm. Làm thủ công mất 2 ngày."

⏱ 1:30–3:30 — LIVE DEMO
[Mở Dashboard, demo live, KHÔNG slideshow]

⏱ 3:30–4:30 — HOW IT WORKS
"3 AI agent chuyên biệt, powered by BytePlus Seed 2.0..."

⏱ 4:30–5:30 — IMPACT (chỉ dùng số có evidence)
"Trong thử nghiệm với 5 case của chúng tôi: [kết quả thật]."

⏱ 5:30–6:00 — VISION + 90-DAY PILOT
"Top 10 được tham gia Incubation Program với 1:1 mentorship,
pilot doanh nghiệp thật, và kết nối investor.
Kế hoạch: Week 1–2 validate → Month 1 Printway pilot
→ Month 2 tích hợp Kalodata → Month 3: 5–10 R&D users."

⏱ 6:00–7:00 — Q&A Buffer
```

### Evidence Pack — Mỗi số phải có nguồn

> ⚠️ Brand Voice yêu cầu: **KHÔNG phóng đại, KHÔNG bịa số liệu.** Rubric Accuracy = 30/100.

| Metric trong pitch | Value | Source | Sample size | Real / Giả định |
|---|---|---|---|---|
| Thời gian R&D thủ công | [X] giờ/tuần | Hỏi Printway mentor 21/8 | — | ❓ Cần confirm |
| Tỷ lệ SP fail | [Y]% | Hỏi Printway mentor 21/8 | — | ❓ Cần confirm |
| Tiết kiệm thời gian | [Z] giờ | Test 5 case trong hackathon | 5 SP | 📊 Real test |
| Accuracy scoring | [W]% | So AI score vs kết quả đã biết | 5 SP | 📊 Real test |
| ROI/tháng | [V] triệu VND | Tính: time saved × hourly rate | Dựa trên test | 📐 Calculation |

**Quy tắc pitch:**
```
✅ "Trong thử nghiệm với 5 case, chúng tôi tiết kiệm Z giờ..."
❌ "Tiết kiệm 15 giờ/tuần" (không có evidence)
✅ "Dựa trên test, accuracy đạt W%"
❌ "Accuracy tăng từ 30% lên 85%" (bịa baseline)
```

> **Demo live > Video demo > Screenshot > Slide text**

---

## 16. Q&A Bank — Luyện trước

| # | Câu hỏi | Gợi ý trả lời |
|---|---|---|
| 1 | "Data lấy từ đâu?" | "Kalodata API (trending) + web scraping Etsy + KB ngành POD. Mỗi datapoint có source + timestamp" |
| 2 | "AI sai thì sao?" | "Confidence score + evidence chain. User quyết định cuối. Dashboard hiển 'Why this score?'" |
| 3 | "Vì sao score đáng tin?" | "Nhờ mentor Printway gán ground truth cho N SP. [N]/[N] matched." |
| 4 | "Chi phí mỗi analysis?" | **Đo thật**: "Chạy 10 runs, trung bình [X] tokens → ~$[Y]/run dựa trên ModelArk pricing" |
| 5 | "Latency?" | **Đo thật**: "P50 = [X]s, P95 = [Y]s" (ghi benchmark từ hackathon account) |
| 6 | "Scale 10,000 users?" | "Stateless API → horizontal scale. ModelArk auto-scale. Cần stress test thêm" |
| 7 | "Privacy?" | "Dùng ModelArk API (không Playground) → theo ToS của ModelArk API. Không đưa PII. Xác nhận điều khoản cụ thể với BTC" |
| 8 | "Khác ChatGPT?" | "Domain-specific pipeline + 9 chỉ số POD + multi-agent + evidence chain" |
| 9 | "Sponsor cần SP này?" | "Printway R&D thủ công → tiết kiệm [X]h/tuần. Top 10 vào Incubation + pilot thật" |
| 10 | "Monetize?" | "SaaS $X/tháng. Printway 10,000+ users. 90-day pilot plan sẵn" |
| 11 | "Accuracy?" | "Test N SP với ground truth từ mentor. [N]/[N] matched. Không suy rộng thành system accuracy" |
| 12 | "Production-ready?" | "Core logic ready. Cần: real data pipeline + auth + monitoring + Kalodata integration" |

---

## 17. Sai lầm phổ biến

| Sai lầm | Hậu quả | Cách tránh |
|---|---|---|
| Xây **Chatbot** thay vì Dashboard | Thiếu WOW, không actionable | Dashboard + scoring + calendar |
| Over-engineer features | Demo lỗi | 1 feature hoàn hảo > 10 feature tệ |
| Mock data | GK không tin | Chuẩn bị 3–5 real data points |
| Pitch quá kỹ thuật | GK business không hiểu | 1 GK không biết code phải hiểu |
| Không ngủ | Pitch tệ 40% | Ngủ ≥ 5–6 tiếng |
| Slide giờ cuối | Không kịp | Ai đó làm slide SONG SONG code |
| Thêm feature sáng D2 | Demo hỏng | **KHÔNG thêm feature** sau 6:00 D2 |
| Nhồi instruction vào 1 AI | Hiệu năng tệ | Chia nhỏ agent (Window Zero-sum) |

### Quy tắc 80/20 cho 48 giờ:
```
20% thời gian → 80% impact:
  ✅ Core demo flow end-to-end
  ✅ 1 "wow moment" (Dashboard scoring / Content Calendar)
  ✅ Số liệu business impact
  ✅ BytePlus Seed 2.0 tích hợp sâu

ĐỪNG LÀM:
  ❌ Edge cases       ❌ Perfect UI
  ❌ Feature mới      ❌ Tối ưu performance
```

---

## 18. Demo War Room — Đảm bảo demo không fail

### Checklist độ tin cậy demo:
```
✅ Health-check API một nút (GET /health trả về status + model info)
✅ Cache sẵn 3 case real (output JSON + image/video local)
✅ Lưu output image/video local (video URL Seedance hết hạn sau 24h!)
✅ .env.example có sẵn, không commit key thật
✅ API timeout 60s + retry logic 3 lần + exponential backoff
✅ Chế độ DEMO_MODE: nếu API lỗi → trả cached output thay vì crash
✅ Laptop thứ hai mở sẵn dashboard (đề phòng laptop chính lỗi)
✅ Git tag `demo-stable` trước 9:00 sáng 22/8
✅ Tuyệt đối KHÔNG deploy code mới sau thời điểm freeze (9:00)
✅ Hotspot điện thoại sẵn sàng phòng WiFi venue lag
✅ Backup video screen recording 2–3 phút đã quay trước
```

### Measured Benchmark Sheet (cập nhật khi test)

> `[💡 TEAM]` Chạy 10 runs trên hackathon account thật, ghi lại:

| Metric | Value | Ghi chú |
|---|---|---|
| Success rate | ___ / 10 | Có run nào fail? |
| P50 latency (agent pipeline) | ___s | Seed 2.0 LLM call |
| P95 latency (agent pipeline) | ___s | Worst case |
| Tokens/run (avg) | ___ | Input + output |
| Cost/run | $___  | Tính từ ModelArk pricing thật |
| Seedance concurrency/RPM | ___ | Rate limit hackathon account |
| Seedance avg gen time | ___s | Task submit → video ready |
| Accuracy vs ground truth | ___/N | Mentor-labeled cases |

> ⚠️ Seedance 2.0 có rate limit khác nhau theo account. Benchmark trên hackathon account mới chính xác.

### DEMO_MODE implementation:
```python
# config.py
import os
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Trong agent:
if DEMO_MODE:
    return load_cached_output(product_id)  # trả kết quả đã cache
else:
    return call_llm(prompt)  # gọi API thật
```

---

## 19. Nội quy & đồ mang theo

### Quy định team:
- 3–5 người, có mặt xuyên suốt
- Được phân 1 Buddy + 1 Mentor
- Tuân thủ nội quy BTC

### Quy định kỹ thuật:
- Dùng Git, cập nhật code thường xuyên
- Nộp qua GitHub
- Pre-implementation ≤ 30%

### Mang theo:
| Bắt buộc | Nên mang |
|---|---|
| 💻 Laptop + Sạc | 🔌 Ổ cắm / Dây nối dài |
| 🪪 CCCD | 💧 Bình nước |
| | 🎧 Tai nghe · Chuột · USB |

---

## 20. Nộp bài — chi tiết

**Deadline: 10:00 sáng 22/8** ⏰

### 3 bước nộp:
1. **Code push GitHub** — grant access BTC + tất cả Mentor
2. **Điền Submission Form:** https://yjp0wgk8loyf.jp.larksuite.com/share/base/form/shrjppt2efTYlspZzGU75PK7tdh
3. **Điền Registration Doc:** https://docs.google.com/document/d/1oL2s1eDQD9f1AS21ostP_7Xc2Rm0Gl6x_3bzYKV6ZrA/edit

### Yêu cầu nộp bài chi tiết:
| File / Mục | Yêu cầu | Ghi chú |
|---|---|---|
| **GitHub repo** | Code đầy đủ, chạy được | Grant access cho BTC + Mentor **trước** 10:00 |
| **README.md** | Hướng dẫn cài đặt + chạy + demo | Phải rõ ràng — GK không có thời gian đoán |
| **.env.example** | Template biến môi trường | KHÔNG commit key thật |
| **Submission Form** | Điền đầy đủ tất cả field | Lưu bản nháp trước, submit 1 lần |
| **Registration Doc** | Thông tin đội + mô tả sản phẩm | Viết sẵn từ tối 21/8 |
| **Pitch deck** | ≤ 10 slides, PDF hoặc Google Slides | Link share public |
| **Video backup** | Screen recording demo 2–3 phút | Phòng wifi lag khi pitch |

### Checklist "Powered by BytePlus" (phải có):
```
✅ Ghi "Powered by BytePlus Seed 2.0" trên UI (header hoặc footer)
✅ 1 slide trong pitch deck: "Cách chúng tôi dùng BytePlus"
✅ README ghi rõ: "Built with BytePlus ModelArk — Seed 2.0"
✅ Code có comment rõ chỗ nào gọi BytePlus API
✅ Demo nhắc đến BytePlus ít nhất 1 lần khi giải thích architecture
```

---

## 21. Kế hoạch ngày mai (20/8) + Day 1 (21/8)

### 20/8 — Ngày chuẩn bị

| Giờ | Việc | Ai |
|---|---|---|
| 8:00–9:00 | Xem Webinar BytePlus (Inside AIGC) | Cả đội |
| 9:00–9:45 | Xem Webinar Tony Nguyễn (Vibe Code) | Cả đội |
| 10:00–12:00 | Build boilerplate + test LLM call | Backend |
| 13:00–14:00 | Đọc kỹ đề bài đã chọn | Cả đội |
| 14:00–15:30 | Chuẩn bị 3 case demo thật | Business/PM |
| 15:30–16:30 | Viết prompt mẫu cho agents | Backend |
| 16:30–17:00 | Push boilerplate lên GitHub | Dev |
| 18:00–18:30 | Viết ROI pitch + architecture diagram | Business |
| 18:30–19:00 | Chuẩn bị đồ đạc | Cả đội |
| **Trước 22:00** | **NGỦ ← bắt buộc** | — |

### Day 1 — 21/8 · Phân công giờ cụ thể

| Giờ | Backend (1–2 người) | Frontend (1 người) | Business/PM (1 người) |
|---|---|---|---|
| 08:00–08:30 | Check-in | Check-in | Check-in |
| 08:30–09:00 | Khai mạc · **Hỏi Mentor xin BytePlus key** | Khai mạc | Khai mạc |
| 09:00–10:00 | Setup env + test BytePlus API | Setup UI boilerplate | Chốt scope MVP + viết brief |
| 10:00–11:00 | Build Agent 1 (Research/Scraper) | Thiết kế Dashboard layout | **Tham dự Training 1** — ghi chú |
| 11:00–12:00 | Lunch | Lunch | Lunch |
| 12:00–13:30 | Build Agent 2 (Scorer/Strategy) | Code Dashboard components | Chuẩn bị data demo thật |
| 13:30–14:30 | Build Agent 3 (Creative/Lifecycle) | Nối API → UI | Bắt đầu soạn pitch deck |
| 14:30–15:30 | **Training 2** — ghi chú | **Training 2** — ghi chú | **Training 2** — ghi chú |
| 15:30–16:30 | Nối pipeline end-to-end | Polish UI | Soạn slide pitch |
| 16:30–18:00 | Test + fix bug | Test 3 case demo | Viết ROI + rehearsal pitch |
| **18:00** | **Demo flow end-to-end phải chạy được** | **UI phải hiển thị kết quả** | **Pitch deck draft xong** |

### ⚠️ Backup Plan nếu API lỗi

| Tình huống | Hành động |
|---|---|
| BytePlus key chưa nhận được | Dùng **GPT-4o / Claude** key cá nhân (wrapper code hỗ trợ switch) |
| BytePlus API chậm / timeout | Tăng timeout lên 60s · Thêm retry logic 3 lần |
| BytePlus API lỗi hoàn toàn | Switch sang OpenAI ngay · Ghi "Designed for BytePlus" trong pitch |
| WiFi venue lag | Dùng hotspot điện thoại · Pre-generate output offline |
| Demo crash lúc pitch | Có **backup video** screen recording 2–3 phút đã quay sẵn |

---

## 22. Master Checklist

### Trước sự kiện (19–20/8)
- [ ] Chốt đề bài
- [ ] Phân vai: Backend / Frontend / Pitch
- [ ] Xem 2 webinar (BytePlus + Tony Nguyễn)
- [ ] Đọc kỹ đề: byvn.net/lO63
- [ ] Test BytePlus Seed 2.0 API
- [ ] Boilerplate code chạy được
- [ ] GitHub repo + team access
- [ ] 3 case demo sẵn
- [ ] ROI pitch viết xong
- [ ] Ngủ đủ giấc

### Day 1 — 21/8
- [ ] Lock đề trong 60 phút đầu
- [ ] Phân công task
- [ ] Slide song song với code
- [ ] BytePlus integrate từ sớm
- [ ] Demo flow end-to-end trước 18:00

### Day 2 — 22/8
- [ ] KHÔNG thêm feature mới
- [ ] Real data cho demo
- [ ] Submit trước deadline (10:00 hoặc 10:30 — confirm với BTC)
- [ ] Rehearsal pitch ≥ 3 lần
- [ ] Backup video demo

### Trước pitch
- [ ] BytePlus Seed 2.0 tích hợp ✅
- [ ] Dashboard (không phải chatbot) ✅
- [ ] Demo real data ✅
- [ ] Evidence Pack — mỗi số có source ✅
- [ ] "Powered by BytePlus" trong UI + slide + README ✅
- [ ] Pitch deck ≤ 10 slides ✅

---

## 23. Acceptance Tests

> Tài liệu mạnh về "build cái gì" — phần này bổ sung "chứng minh nó đúng".

### PW1 — Hai tầng kiểm thử:

**Tầng 1: Demo Validation (5 case — chuẩn bị sẵn)**
| # | Sản phẩm | Kết quả kỳ vọng | Dùng để test |
|---|---|---|---|
| 1 | Áo thun Graphic Halloween | ✅ NÊN làm (mùa vụ + trend lên) | Happy path |
| 2 | Phone case POD basic | ✅ NÊN làm (evergreen + margin tốt) | Evergreen case |
| 3 | Thiệp Giáng sinh (tháng 8) | ❌ KHÔNG nên (lệch mùa vụ) | Seasonality check |
| 4 | Áo hoodie oversized | ❌ KHÔNG nên (cạnh tranh quá cao) | Competition check |
| 5 | Tote bag eco-friendly | ❓ Ambiguous (margin thấp, trend lên) | Edge case |

**Tầng 2: Batch Evaluation (10–20 case — nhờ mentor Day 1)**
> Sáng 21/8: nhờ **mentor Printway** gán ground truth cho 10–20 SP:
> - Verdict: NÊN / KHÔNG NÊN
> - Lifecycle stage
> - 2–3 chỉ số quan trọng (demand, competition, seasonality)
>
> Chạy batch → so kết quả AI vs mentor labels.

**Quy tắc pitch accuracy:** `[💡 TEAM]`
```
✅ "5/5 demo cases matched mentor labels"
✅ "Batch evaluation: [X]/[N] cases matched"
❌ "Accuracy 100%" (không suy rộng từ mẫu nhỏ)
❌ "Accuracy 85%" (không bịa số)
```

### PW2 — Test chất lượng:
| Test case | Pass criteria |
|---|---|
| Hallucination check | Không bịa số liệu, không hứa hẹn viển vông |
| Brand Voice consistency | 5/5 đặc điểm Printway đều có trong output |
| Cross-channel consistency | Cùng 1 brief → TikTok/FB/Email đều nhất quán thông điệp |
| Hook quality | TikTok hook < 3 giây, có CTA rõ |

---



## 24. Links & Liên hệ

### Links
| Link | Mô tả |
|---|---|
| https://aiglobal.dev | 🌐 Website chính thức |
| https://canva.link/sotaythisinh2026 | 📖 Sổ tay thí sinh |
| https://byvn.net/lO63 | 📋 **6 đề bài chi tiết** |
| https://yjp0wgk8loyf.jp.larksuite.com/share/base/form/shrjppt2efTYlspZzGU75PK7tdh | 📤 **Form nộp bài** |
| https://docs.google.com/document/d/1oL2s1eDQD9f1AS21ostP_7Xc2Rm0Gl6x_3bzYKV6ZrA/edit | 📝 Registration Doc |
| https://luma.com/vzfbgwr5 | 📅 Summit 22/8 |
| https://docs.byteplus.com/api/docs/ModelArk | 📘 BytePlus API Docs |

### Webinar
| Video | Link |
|---|---|
| 🎥 Vibe Code (Tony Nguyễn) | https://youtu.be/JRZ4P5dn3Io |
| 🎥 Inside AIGC (BytePlus) | https://youtu.be/YIn80NTREws |
| 🎥 Printway #1: Product Hub | https://youtu.be/IuJkE-I-SQo |
| 🎥 Printway #2: Content Hub | https://youtu.be/nFBRJ9HBwsw |

### BytePlus
```
Endpoint: your_endpoint_id_here
Base URL: https://ark.ap-southeast.bytepluses.com/api/v3
Models:   Seed 2.0 (LLM) · Seedream 5.0 Lite (Image) · Seedance 2.0 (Video)
Seedance Model ID: dreamina-seedance-2-0-260128
API Key:  [nhận từ BTC]
```

### BTC
| Người | SĐT | Email |
|---|---|---|
| **Ms. Yến Nhi** | +84 905 780 862 | yennhi.nguyen@dnes.vn |
| **Ms. Vi Trần** | +84 963 653 208 | — |

---

> ### 🔥 6 ĐIỀU THEN CHỐT
> 1. **Dashboard > Chatbot** — BTC nói rõ
> 2. **Accuracy 30/100** — mỗi số phải có evidence, không bịa
> 3. **Seed 2.0 Omni** = multi-modal — tận dụng để differentiate
> 4. **Mỗi agent 1 việc** (Window Zero-sum)
> 5. **Seedance = async API** — đừng gọi sync, sẽ timeout
> 6. **Xác nhận deadline + Top 8/10 với BTC sáng 20/8**

---
*v6 War-Room Ready · 20/08/2026 00:00*  
*Nguồn: Sổ tay thí sinh · 4 Webinar · aiglobal.dev · Luma · BytePlus Docs*
