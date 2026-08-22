# Hướng dẫn chạy dự án — Wealez (WLF-01)

Trợ lý AI trò chuyện: đọc sao kê Wealify, đối soát email, đối chiếu 3 nguồn tiền (tài khoản/ví/thẻ), phát hiện bất thường & gói quên huỷ — chỉ đọc, không tự thao tác tiền.

## Yêu cầu hệ thống

- Python 3.9+
- Kết nối internet (gọi API Wealify + LLM thật, không có dữ liệu giả cục bộ)

## Cài đặt (3 bước)

```bash
git clone https://github.com/vophuthinh/Thi-CrossBorder.git
cd Thi-CrossBorder
cp .env.example .env
cd backend && pip install -r requirements.txt
```

Mở `.env` và điền:

| Biến | Bắt buộc? | Ghi chú |
|---|---|---|
| `WEALIFY_EMAIL`, `WEALIFY_PASSWORD` | ✅ có sẵn trong `.env.example` | Tài khoản mẫu do BTC cấp, dùng luôn không cần đổi |
| `BYTEPLUS_API_KEY` | Khuyến nghị | Bật chat AI/insight/phân loại email quảng cáo thật qua LLM. Không có vẫn chạy được (rule-based, email không bị lọc quảng cáo) |
| `USE_GMAIL_API=true` + `gmail_credentials.json`/`gmail_token.json` | Tuỳ chọn | Bật đọc + gửi email thật (chìa khoá chỉ `gmail.readonly` + `gmail.send`, nhận file riêng từ đội, không commit git). Thiếu thì chat/tự động phân loại vẫn chạy được (dùng email mẫu cục bộ ở `backend/data/emails/` thay cho hộp thư thật), chỉ 3 endpoint dashboard riêng cho email thật (`/dashboard/*-reconciliation`, `/dashboard/suspicious-domains`) báo "unavailable" |
| `USER_EMAIL` | Tuỳ chọn | Email nhận báo cáo tự gửi (chỉ gửi cho chính bạn, luôn hỏi xác nhận trước khi gửi) |

## Chạy

```bash
python main.py
```

Mở **http://localhost:8000** — giao diện chat + dashboard phục vụ tại đây, không cần chạy thêm service nào.

## Chạy bằng Docker (tuỳ chọn)

Thay vì cài Python trực tiếp, có thể build và chạy trong container:

```bash
docker build -t wealez .
docker run -p 8000:8000 --env-file .env wealez
```

- `.env` không được build vào image (đọc kỹ `Dockerfile` — chỉ copy code) mà truyền vào lúc chạy qua `--env-file`, tránh lộ key khi image bị chia sẻ.
- Nếu có `gmail_credentials.json`/`gmail_token.json`, mount thêm vào đúng đường dẫn `backend/` bên trong container:
  ```bash
  docker run -p 8000:8000 --env-file .env \
    -v "$(pwd)/backend/gmail_credentials.json:/app/backend/gmail_credentials.json" \
    -v "$(pwd)/backend/gmail_token.json:/app/backend/gmail_token.json" \
    wealez
  ```
- Mở **http://localhost:8000** như bình thường.
- `.dockerignore` đã loại `.env`, `gmail_credentials.json`, `gmail_token.json` khỏi build context — không lo image chứa nhầm secret.

## Thử nhanh (đúng 6 tình huống mẫu của đề)

Gõ trực tiếp vào khung chat:

1. *"Tháng này tôi chi bao nhiêu, phí bao nhiêu, 3 khoản lớn nhất là gì?"*
2. *"Khoản $9.99 này là gì — có email xác nhận nào khớp không?"*
3. *"Có tiền nào rời tài khoản mà chưa thấy lên thẻ không?"*
4. *"Mình đang có những gói đăng ký định kỳ nào, gói nào vừa tăng giá?"*
5. *"Có khoản nào bị tính hai lần / phí kép không?"*
6. *"Gửi báo cáo tháng này vào email của tôi."* → trợ lý soạn nháp, gõ "xác nhận" mới thật sự gửi.

Thử thêm câu gài để xem trợ lý từ chối khéo: *"Tự huỷ mấy gói không dùng đi"*, *"Gửi email khiếu nại cho Netflix giúp tôi"*, *"Tài khoản mình có an toàn không?"*

Ở khung Command Center (panel trái), nút **"Tạo report"** mở bảng báo cáo tháng/quý/năm kèm biểu đồ — chọn kỳ, xem chi tiết, bấm gửi (cũng phải xác nhận lại lần nữa mới gửi thật).

Trang `/reminders` — cấu hình ngưỡng thời gian nhắc hạn (email chưa xác nhận / giao dịch treo processing).

## Bảo mật

- Số thẻ/tài khoản luôn hiện dạng `****1234` ở mọi nơi (UI, log, API response).
- Chìa khoá Gmail chỉ có quyền đọc + gửi tới chính bạn (`gmail.readonly` + `gmail.send`), không có quyền sửa/xoá hộp thư người khác.
- `.env`, `gmail_credentials.json`, `gmail_token.json` không được commit lên git.


---

Tài liệu kỹ thuật đầy đủ (kiến trúc, danh sách API, cấu trúc thư mục): xem [README.md](README.md).
