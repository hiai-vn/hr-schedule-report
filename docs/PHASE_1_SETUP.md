# Phase 1: Hướng Dẫn Cài Đặt và Cấu Hình

Tài liệu này hướng dẫn chi tiết cách thiết lập môi trường cho hệ thống AI Thống kê Ngày công từ Telegram.

## 1. Yêu cầu hệ thống

*   Python 3.8 trở lên.
*   Kết nối Internet ổn định.

## 2. Cài đặt thư viện

Mở terminal tại thư mục gốc của dự án và chạy lệnh sau để cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## 3. Lấy thông tin API

### 3.1. Telegram API (Bắt buộc)
Để truy cập tin nhắn Telegram, bạn cần tạo một ứng dụng trên Telegram:

1.  Truy cập [https://my.telegram.org](https://my.telegram.org).
2.  Đăng nhập bằng số điện thoại của bạn.
3.  Chọn **API development tools**.
4.  Điền thông tin vào form (App title, Short name...).
5.  Sau khi tạo xong, bạn sẽ thấy `App api_id` và `App api_hash`. Hãy lưu lại hai thông tin này.

### 3.2. Gemini API (Cho Phase 3)
Để sử dụng AI phân tích tin nhắn:

1.  Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey).
2.  Tạo một API Key mới.
3.  Lưu lại API Key.

## 4. Cấu hình Môi trường

1.  Sao chép file `.env.example` thành file `.env`:
    *   **Windows:** `copy .env.example .env`
    *   **Linux/Mac:** `cp .env.example .env`

2.  Mở file `.env` bằng trình soạn thảo văn bản và điền thông tin đã lấy ở bước 3:

```ini
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=abcdef123456...
GEMINI_API_KEY=AIzaSyD...
# Để trống các trường TARGET_GROUP_ID và TARGET_TOPIC_ID tạm thời
TARGET_GROUP_ID=
TARGET_TOPIC_ID=
SESSION_NAME=telegram_session
```

## 5. Xác thực Telegram

Chạy script sau để đăng nhập vào tài khoản Telegram của bạn và tạo file session:

```bash
python scripts/telegram_auth.py
```

*   Nhập số điện thoại của bạn (định dạng quốc tế, ví dụ `+84...`).
*   Nhập mã xác thực (OTP) được gửi về ứng dụng Telegram trên điện thoại.
*   Nếu bạn có bật xác thực 2 bước (2FA), hãy nhập mật khẩu khi được yêu cầu.

Sau khi đăng nhập thành công, file `telegram_session.session` sẽ được tạo ra tại thư mục gốc. **Tuyệt đối không chia sẻ file này cho người khác.**

## 6. Lấy ID Nhóm và Topic

Để bot biết cần lấy dữ liệu từ nhóm nào, bạn cần lấy ID của nhóm và Topic "Schedule".

1.  Chạy script sau:

```bash
python scripts/get_dialog_info.py
```

2.  Script sẽ liệt kê danh sách các nhóm và topic (nếu là Forum) mà bạn tham gia.
3.  Tìm tên nhóm làm việc của bạn.
4.  Copy `ID` của nhóm và `Topic ID` (nếu có).
    *   **Lưu ý:** ID của nhóm thường là số âm (ví dụ `-100123456789`).

5.  Quay lại file `.env` và cập nhật thông tin:

```ini
TARGET_GROUP_ID=-100123456789
TARGET_TOPIC_ID=123  # Nếu không dùng Topic (nhóm thường), để trống hoặc xóa dòng này
```

## 7. Kiểm tra cấu hình

Sau khi điền đầy đủ, cấu hình của bạn đã hoàn tất. Hệ thống đã sẵn sàng cho Phase 2 (Thu thập dữ liệu).
