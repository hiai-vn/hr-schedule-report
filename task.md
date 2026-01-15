# Hệ thống AI Thống kê Ngày công từ Telegram

**Mục tiêu:** Xây dựng hệ thống tự động sử dụng AI để truy vấn, phân tích dữ liệu lịch làm việc từ topic "Schedule" trong các nhóm Telegram và xuất báo cáo thống kê ngày công (đi làm, nghỉ, trễ, nửa buổi, remote) ra file Excel/Google Sheet hàng tháng.

**Phạm vi:** Áp dụng cho các bạn thực tập sinh và nhân viên đang làm việc tại văn phòng.

---

## I. Phase 1: Khởi tạo và Cấu hình (Initialization and Configuration)

| ID | Nhiệm vụ (Task) | Mô tả chi tiết | Ưu tiên | Thời gian ước tính |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | **Thiết lập Môi trường Phát triển** | Cài đặt Python, các thư viện cần thiết (Telethon/Pyrogram, Pandas, openpyxl, thư viện AI/NLP). | Cao | 1 ngày |
| **1.2** | **Đăng ký Telegram API** | Đăng ký tài khoản Telegram để lấy `API ID` và `API Hash` cần thiết cho việc truy cập MTProto API (để đọc tin nhắn nhóm). | Cao | 0.5 ngày |
| **1.3** | **Cấu hình Kết nối Telegram** | Viết script kết nối và xác thực với Telegram bằng `API ID` và `API Hash`. Đảm bảo có thể truy cập được các nhóm mục tiêu. | Cao | 1 ngày |
| **1.4** | **Xác định Group và Topic ID** | Lấy chính xác `Group ID` của các nhóm làm việc và `Topic ID` (hoặc `message_thread_id`) của topic "Schedule" trong các nhóm đó. | Cao | 0.5 ngày |

## II. Phase 2: Thu thập Dữ liệu (Data Collection) - (Completed)

| ID | Nhiệm vụ (Task) | Mô tả chi tiết | Ưu tiên | Thời gian ước tính |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | **Truy vấn Tin nhắn** | Viết hàm sử dụng thư viện client (Telethon/Pyrogram) để truy vấn tất cả tin nhắn trong một khoảng thời gian nhất định (ví dụ: 1 tháng) từ `Group ID` và `Topic ID` đã xác định. | Cao | 1 ngày |
| **2.2** | **Lọc Tin nhắn Ban đầu** | Lọc bỏ các tin nhắn không liên quan (ví dụ: tin nhắn hệ thống, tin nhắn quá ngắn) và chỉ giữ lại các tin nhắn có khả năng chứa thông tin lịch làm việc. | Trung bình | 0.5 ngày |
| **2.3** | **Lưu trữ Dữ liệu Thô** | Lưu trữ dữ liệu tin nhắn thô (bao gồm ID người gửi, thời gian, nội dung tin nhắn) vào cơ sở dữ liệu tạm thời (ví dụ: SQLite) hoặc file JSON để dễ dàng xử lý lại. | Trung bình | 0.5 ngày |

## III. Phase 3: Xử lý Ngôn ngữ Tự nhiên (NLP/AI Processing)

| ID | Nhiệm vụ (Task) | Mô tả chi tiết | Ưu tiên | Thời gian ước tính |
| :--- | :--- | :--- | :--- | :--- |
| **3.1** | **Xây dựng/Chọn mô hình AI/NLP** | Lựa chọn mô hình AI (ví dụ: mô hình ngôn ngữ lớn như GPT-4, Gemini, hoặc mô hình NLP tùy chỉnh) để phân tích nội dung tin nhắn. | Cao | 2 ngày |
| **3.2** | **Thiết kế Prompt/Logic Trích xuất** | Thiết kế prompt (đối với LLM) hoặc logic trích xuất (đối với mô hình tùy chỉnh) để xác định các thông tin sau từ mỗi tin nhắn: <br> - **Tên nhân viên/thực tập sinh** <br> - **Ngày áp dụng** <br> - **Loại hình làm việc:** `Đi làm`, `Nghỉ`, `Trễ`, `Nửa buổi`, `Remote` | Cao | 2 ngày |
| **3.3** | **Xử lý Biến thể Ngôn ngữ** | Đảm bảo mô hình có thể xử lý các biến thể ngôn ngữ tự nhiên trong tiếng Việt (ví dụ: "đi làm trễ", "late", "off", "wfh", "làm việc tại nhà", "nghỉ phép", "về sớm"). | Cao | 1.5 ngày |
| **3.4** | **Kiểm thử và Đánh giá Độ chính xác** | Kiểm thử mô hình với một tập dữ liệu mẫu và đánh giá độ chính xác của việc trích xuất thông tin. Tinh chỉnh lại prompt/logic nếu cần. | Cao | 1 ngày |
| **3.5** | **Chuẩn hóa Dữ liệu** | Chuyển đổi dữ liệu trích xuất thành định dạng chuẩn hóa (ví dụ: `[Tên, Ngày, Loại hình]`) sẵn sàng cho việc thống kê. | Trung bình | 0.5 ngày |

## IV. Phase 4: Lưu trữ và Báo cáo (Storage and Reporting)

| ID | Nhiệm vụ (Task) | Mô tả chi tiết | Ưu tiên | Thời gian ước tính |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | **Thiết kế Cấu trúc Dữ liệu Báo cáo** | Thiết kế cấu trúc bảng thống kê cuối cùng (ví dụ: Cột `Tên`, `Tổng ngày làm`, `Tổng ngày nghỉ`, `Tổng ngày trễ`, v.v.). | Trung bình | 0.5 ngày |
| **4.2** | **Thống kê Dữ liệu** | Viết script để tổng hợp dữ liệu đã chuẩn hóa (từ Phase 3) theo từng nhân viên và từng loại hình làm việc trong tháng. | Cao | 1 ngày |
| **4.3** | **Tạo Báo cáo Excel** | Sử dụng thư viện Pandas/openpyxl để tạo file Excel (`.xlsx`) từ dữ liệu thống kê. Đảm bảo định dạng dễ đọc và có tiêu đề rõ ràng. | Cao | 1 ngày |
| **4.4** | **Tích hợp Google Sheets (Tùy chọn)** | Nếu cần Google Sheets, thiết lập kết nối API (Google Sheets API) và viết script để tự động tải dữ liệu lên một Sheet đã định sẵn. | Trung bình | 1.5 ngày |

## V. Phase 5: Vận hành và Bảo trì (Operation and Maintenance)

| ID | Nhiệm vụ (Task) | Mô tả chi tiết | Ưu tiên | Thời gian ước tính |
| :--- | :--- | :--- | :--- | :--- |
| **5.1** | **Tự động hóa Lịch trình** | Thiết lập cron job hoặc dịch vụ lập lịch (ví dụ: Windows Task Scheduler, Linux Cron) để chạy toàn bộ quy trình (từ Phase 2 đến Phase 4) vào cuối mỗi tháng. | Cao | 1 ngày |
| **5.2** | **Xử lý Lỗi và Thông báo** | Xây dựng cơ chế ghi log và thông báo lỗi (ví dụ: gửi email hoặc tin nhắn Telegram) nếu quá trình tự động hóa thất bại. | Trung bình | 0.5 ngày |
| **5.3** | **Bảo trì và Cập nhật** | Lên kế hoạch định kỳ kiểm tra và cập nhật các tham số trích xuất AI/NLP khi có sự thay đổi về cách thức ghi lịch làm việc trong nhóm Telegram. | Thấp | Liên tục |

---

**Tổng thời gian ước tính:** Khoảng **15 - 17 ngày làm việc** (không bao gồm thời gian chờ phản hồi API hoặc tinh chỉnh mô hình AI phức tạp).

**Ghi chú:**
*   Việc truy cập tin nhắn lịch sử trong nhóm Telegram **bắt buộc** phải sử dụng **MTProto API** thông qua các thư viện client như **Telethon** hoặc **Pyrogram**, không thể dùng Bot API thông thường.
*   Độ chính xác của hệ thống phụ thuộc rất lớn vào chất lượng của **Prompt/Logic Trích xuất** trong Phase 3. Cần có một tập dữ liệu mẫu lớn để huấn luyện hoặc tinh chỉnh (fine-tune) mô hình AI.
