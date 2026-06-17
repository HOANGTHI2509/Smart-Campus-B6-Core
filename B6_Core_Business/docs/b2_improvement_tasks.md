# Kế hoạch Nâng cấp Hệ thống: Tối ưu luồng dữ liệu Camera (B2)

Tài liệu này liệt kê các chiến lược nâng cấp dành riêng cho luồng dữ liệu Camera Stream (B2). Mục tiêu là biến B6 thành một "Bộ Não" phân tích ngữ cảnh thông minh thay vì chỉ nhận và chuyển tiếp dữ liệu.

---

## 🛠 Task 1: Bộ Lọc An Ninh Theo Khung Giờ (Time-based Policy Engine)
**Vấn đề:** Hiện tại, hễ B2 phát hiện có chuyển động (`motion_detected: true`) là B6 cảnh báo. Nhưng nếu là giờ hành chính thì việc có chuyển động là bình thường.
**Giải pháp:** Áp dụng luật thời gian (Time-based Rules) để đánh giá mức độ rủi ro.

*   **Sub-task 1.1:** Xây dựng bảng thời gian hoạt động (Operating Hours) cho từng khu vực. (Ví dụ: Hành lang `06:00 - 22:00` là Normal, `22:00 - 06:00` là Restricted).
*   **Sub-task 1.2:** Cập nhật hàm xử lý: Khi nhận event từ B2, lấy thời gian thực (`datetime.now()`) đối chiếu với bảng Operating Hours.
*   **Sub-task 1.3:** 
    *   Nếu có chuyển động ngoài giờ hành chính ➡️ Bật còi báo động B7 (Intruder Alert).
    *   Nếu trong giờ hành chính ➡️ Chỉ ghi log vào Database (INFO).

---

## 🛠 Task 2: Giao Thoa Dữ Liệu B2 & B3 (Cross-Service Validation)
**Vấn đề:** Làm sao biết một người đang đứng trong phòng Server là kỹ thuật viên hay là kẻ trộm lẻn vào?
**Giải pháp:** Đối chiếu chéo dữ liệu của Camera (B2) và Cổng An Ninh (B3).

*   **Sub-task 2.1:** Lưu trạng thái căn phòng vào biến (hoặc DB): Phòng Server hiện tại có bao nhiêu người quẹt thẻ B3 thành công để đi vào.
*   **Sub-task 2.2:** Khi Camera B2 báo cáo "Có bóng người trong phòng Server", B6 sẽ kiểm tra DB.
*   **Sub-task 2.3:** Nếu DB báo "Chưa có ai quẹt thẻ vào phòng này cả" ➡️ Khẳng định đây là kẻ xâm nhập vượt rào (Không quẹt thẻ) ➡️ Báo động mức CRITICAL.

---

## 🛠 Task 3: Điều Phối Phân Tích Khuôn Mặt (Orchestrating AI)
**Vấn đề:** Nếu Camera B2 lúc nào cũng truyền video cho B4 AI phân tích thì sẽ làm sập Server AI vì quá tải GPU.
**Giải pháp:** B6 đóng vai trò Điều phối viên (Orchestrator). AI chỉ được bật khi B6 cho phép.

*   **Sub-task 3.1:** B6 nhận tín hiệu MQTT `motion_detected: true` từ B2 (Tín hiệu cực nhẹ, không tốn băng thông).
*   **Sub-task 3.2:** Thay vì B2 tự gọi B4, B6 sẽ chủ động gọi API sang nhóm B4 (AI Vision) với lệnh: *"Này B4, tao vừa thấy có chuyển động ở CAM-001, mày bật model nhận diện khuôn mặt lên quét ngay cho tao!"*
*   **Sub-task 3.3:** Nhờ vậy, B4 tiết kiệm được 90% tài nguyên máy chủ, và Thầy giáo sẽ cực kỳ nể phục khả năng điều phối "Tiết kiệm năng lượng" của nhóm bạn.

---

## 🛠 Task 4: Lưu Trữ Bằng Chứng Hình Ảnh (Evidence Storage)
**Vấn đề:** Khi bảo vệ nhận được cảnh báo, họ cần xem hình ảnh ngay lập tức để xác minh.
**Giải pháp:** B6 hứng link ảnh do B2 cung cấp để làm bằng chứng.

*   **Sub-task 4.1:** Mở rộng Database, thêm cột `evidence_url` vào bảng Logs.
*   **Sub-task 4.2:** Khi nhận Payload từ B2 qua API `/camera-events`, bóc tách trường `frameData.url`.
*   **Sub-task 4.3:** Lưu trữ URL này, đồng thời gửi đính kèm URL này trong tin nhắn bắn sang B7 để bảo vệ có thể click vào xem ảnh trực tiếp trên điện thoại.
