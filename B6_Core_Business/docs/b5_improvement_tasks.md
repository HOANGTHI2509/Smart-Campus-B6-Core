# Kế hoạch Nâng cấp Hệ thống: Tối ưu luồng dữ liệu Analytics (B5)

Tài liệu này đề xuất các tính năng kiến trúc hệ thống dành riêng cho luồng giao tiếp giữa B6 (Core Business) và B5 (Analytics). Vì B5 là nơi hứng toàn bộ dữ liệu của toàn trường để vẽ biểu đồ, B6 cần đóng vai trò là một "Hệ thống đường ống dữ liệu" (Data Pipeline) thông minh và tối ưu.

---

## 🛠 Task 1: Micro-Batching (Gom nhóm dữ liệu)
**Vấn đề:** Nếu trường có 10.000 sinh viên quẹt thẻ và 500 cảm biến gửi dữ liệu mỗi giây, việc B6 gọi API sang B5 cho từng sự kiện sẽ tạo ra hàng chục ngàn Request, làm sập máy chủ B5 ngay lập tức.
**Giải pháp:** B6 gom các sự kiện nhỏ lẻ lại thành một cục lớn trước khi gửi.

*   **Sub-task 1.1:** Tạo một mảng (List) trên RAM của B6 có tên là `analytics_buffer`.
*   **Sub-task 1.2:** Mỗi khi có quẹt thẻ hoặc báo cáo nhiệt độ, B6 không gọi B5 ngay mà nhét (append) dữ liệu đó vào `analytics_buffer`.
*   **Sub-task 1.3:** Đặt một bộ đếm thời gian (Cronjob/Background Task): Cứ đúng 5 phút một lần, B6 gói toàn bộ mảng `analytics_buffer` thành 1 cục JSON bự và bắn duy nhất 1 Request sang B5. Nhờ vậy, B5 chạy mượt mà không bao giờ bị nghẽn mạng.

---

## 🛠 Task 2: Data Anonymization (Ẩn danh hóa dữ liệu riêng tư)
**Vấn đề:** B5 chỉ cần vẽ biểu đồ "Số lượng người qua cổng". Nếu B6 gửi kèm cả Tên, Lớp, Mã Thẻ của sinh viên sang B5 thì sẽ vi phạm nghiêm trọng luật bảo mật quyền riêng tư (Data Privacy).
**Giải pháp:** B6 đóng vai trò màng lọc bảo mật (Security Filter).

*   **Sub-task 2.1:** Trước khi đẩy dữ liệu sang B5, B6 tiến hành làm sạch dữ liệu (Data Cleansing).
*   **Sub-task 2.2:** Xóa bỏ các trường nhạy cảm như `student_name`, `phone_number`. Mã hóa (Hash) trường `uid` thẻ từ thành một chuỗi ký tự ẩn danh.
*   **Sub-task 2.3:** B5 nhận được dữ liệu vẫn đếm được số lượng người nhưng tuyệt đối không biết họ là ai.

---

## 🛠 Task 3: Data Aggregation (Tính toán sơ bộ - Tiết kiệm dung lượng)
**Vấn đề:** Cảm biến nhiệt độ B1 gửi dữ liệu mỗi giây 1 lần (3.600 dòng log/1 giờ). Gửi toàn bộ 3.600 dòng này cho B5 là lãng phí ổ cứng.
**Giải pháp:** B6 tính toán nháp trước khi gửi.

*   **Sub-task 3.1:** B6 cộng dồn 3.600 dòng nhiệt độ của Lab A101 trong 1 giờ qua.
*   **Sub-task 3.2:** B6 tính ra 3 chỉ số: `Nhiệt độ Trung bình`, `Nhiệt độ Cao nhất`, `Nhiệt độ Thấp nhất`.
*   **Sub-task 3.3:** B6 chỉ gửi duy nhất 1 dòng dữ liệu tóm tắt này sang B5. Nhờ đó, B5 tiết kiệm được 99% dung lượng ổ cứng mà biểu đồ vẽ ra vẫn mượt và chính xác.

---

## 🛠 Task 4: Dead Letter Queue (Hàng đợi chống mất mát dữ liệu)
**Vấn đề:** Lỡ đúng lúc B6 đang gom 1.000 dữ liệu để gửi sang B5 thì máy chủ B5 bị sập (cúp điện, rớt mạng). Dữ liệu sẽ bị mất vĩnh viễn, làm biểu đồ của trường bị khuyết 1 lỗ hổng.
**Giải pháp:** Xây dựng cơ chế chống mất dữ liệu (DLQ).

*   **Sub-task 4.1:** Khi B6 gọi API sang B5 mà bị lỗi `Timeout` hoặc `500 Server Error`.
*   **Sub-task 4.2:** B6 lập tức ghi toàn bộ 1.000 dòng dữ liệu đó ra một file `.json` dự phòng cất tạm vào ổ cứng của B6.
*   **Sub-task 4.3:** Viết một hàm tự động chạy ngầm: Cứ 10 phút kiểm tra xem B5 đã "sống" lại chưa. Nếu B5 sống lại, B6 lấy file `.json` dự phòng ra bắn gửi bù lại cho B5. Tuyệt đối không để rơi rớt 1 byte dữ liệu nào!
