# Xác định TARGET_TOPIC_ID (message_thread_id)

TARGET_TOPIC_ID là ID của chủ đề (Topic) trong nhóm chat có bật tính năng Topics (Diễn đàn). ID này là một số nguyên dương và thường là ID của tin nhắn đầu tiên trong chủ đề đó.

## Phương pháp 1: Phân tích Liên kết Tin nhắn (Đáng tin cậy nhất)

1. **Gửi Tin nhắn vào Topic**: Gửi một tin nhắn bất kỳ vào Topic "Schedule" trong nhóm.

2. **Sao chép Liên kết Tin nhắn**: Nhấp chuột phải vào tin nhắn đó và chọn "Copy Message Link".

3. **Phân tích Liên kết**: Liên kết sẽ có dạng: `https://t.me/c/1234567890/123/456`

   - **Số thứ hai** (ví dụ: `123`) là ID của tin nhắn đầu tiên trong Topic, tức là TARGET_TOPIC_ID (hoặc message_thread_id)
   - **Số thứ ba** (ví dụ: `456`) là ID của tin nhắn bạn vừa gửi

## Phương pháp 2: Sử dụng Thư viện Client (Telethon/Pyrogram)

Sau khi kết nối thành công bằng thư viện client (sử dụng MTProto API), bạn có thể dùng các hàm của thư viện để liệt kê các Topic trong nhóm và lấy ID của chúng.

- **Telethon**: Sử dụng hàm `client.get_discussion_messages()` hoặc tương đương để truy vấn tin nhắn trong một Topic cụ thể

- **Pyrogram**: Sử dụng hàm `client.get_discussion_messages()` hoặc các phương thức liên quan đến ForumTopic

## Phương pháp 3: Sử dụng Script Tự động (Khuyến nghị)

1. **Đảm bảo bạn đã cấu hình API**: Kiểm tra file `.env` đã có `TELEGRAM_API_ID` và `TELEGRAM_API_HASH` (lấy từ [my.telegram.org](https://my.telegram.org))

2. **Chạy script lấy thông tin**: Mở terminal và chạy lệnh sau:
   ```bash
   python scripts/get_dialog_info.py
   ```

3. **Lấy ID**:
   - Script sẽ in ra danh sách các nhóm và topic của bạn trên màn hình
   - Tìm tên nhóm làm việc của bạn và copy ID (với Group, ID thường là số âm)
   - Nếu nhóm là dạng Forum (có Topics), script cũng sẽ liệt kê các Topic bên trong. Tìm topic "Schedule" (hoặc tên tương ứng) và copy ID của nó

4. **Cập nhật cấu hình**: Dán các giá trị ID vừa lấy được vào file `.env` của bạn:
   ```env
   TARGET_GROUP_ID=<Group ID vừa copy>
   TARGET_TOPIC_ID=<Topic ID vừa copy>
   ```