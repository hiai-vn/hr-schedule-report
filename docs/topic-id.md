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

