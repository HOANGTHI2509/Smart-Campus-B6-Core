# Kế hoạch Nâng cấp Hệ thống: Tối ưu luồng dữ liệu Notification (B7)

Tài liệu này đề xuất các tính năng kiến trúc hệ thống chuyên sâu nhằm đảm bảo luồng giao tiếp giữa B6 (Core Business) và B7 (Notification) luôn ở trạng thái ổn định và đáng tin cậy nhất. Vì B7 là "Còi báo cháy" của toàn trường, việc đánh rơi tin nhắn là điều tối kỵ.

---

## 🛠 Task 1: Ngăn Chặn Bão Cảnh Báo (Alert Storm Prevention / Correlation)
**Vấn đề:** Khi có cháy thực sự ở Lab A101, Cảm biến nhiệt (B1) báo cháy, Camera (B2) thấy có chuyển động hỗn loạn, AI (B4) thấy lửa. B6 sẽ kích hoạt 3 sự kiện dội bom sang B7 cùng lúc khiến bảo vệ hoang mang không biết chuyện gì đang xảy ra.
**Giải pháp:** B6 đóng vai trò Tổng hợp & Tương quan sự kiện (Alert Correlation).

*   **Sub-task 1.1:** Khi nhận một cảnh báo, B6 mở một "Cửa sổ thời gian" (Time window) khoảng 30 giây.
*   **Sub-task 1.2:** Nhóm tất cả các cảnh báo từ B1, B2, B4 xảy ra trong 30 giây đó tại cùng 1 khu vực (Lab A101) vào làm 1.
*   **Sub-task 1.3:** Đóng gói và gửi duy nhất 1 tin nhắn cực kỳ chất lượng sang B7: *"CRITICAL: Hỏa hoạn tại Lab A101. Đã được xác nhận chéo bởi Cảm biến nhiệt độ, Camera và AI Vision!"*.

---

## 🛠 Task 2: Cơ chế Thử lại thông minh (Exponential Backoff Retry)
**Vấn đề:** Lúc có cháy, lỡ mạng chập chờn hoặc máy B7 bị treo 1 giây. B6 gửi API thất bại và... bỏ qua luôn. Chuông không kêu và trường bị thiêu rụi!
**Giải pháp:** Báo cháy là sự kiện sống còn, B6 phải "cố đấm ăn xôi" gửi bằng được.

*   **Sub-task 2.1:** Viết một vòng lặp `while/try-catch` bọc bên ngoài hàm `call_b7_notify`.
*   **Sub-task 2.2:** Áp dụng thuật toán **Exponential Backoff**: Nếu gửi lỗi, chờ 1 giây rồi gửi lại. Vẫn lỗi? Chờ 2 giây rồi gửi lại. Vẫn lỗi? Chờ 4 giây rồi gửi lại... lặp lại tối đa 5 lần.
*   **Sub-task 2.3:** Bằng cách này, B6 vừa không làm sập B7 (vì có thời gian nghỉ), vừa đảm bảo 99.9% tin nhắn báo cháy sẽ lọt qua được cửa tường lửa.

---

## 🛠 Task 3: Giám Sát Nhịp Tim (Heartbeat / Health-check)
**Vấn đề:** Làm sao B6 biết hệ thống loa báo động của trường (B7) vẫn đang cắm điện hay đã bị kẻ gian cắt dây cáp mạng?
**Giải pháp:** B6 phải liên tục "bắt mạch" B7.

*   **Sub-task 3.1:** Chạy một hàm ngầm (Background Task) trên B6. Cứ mỗi 1 phút, B6 sẽ gửi một request `GET /health` nhẹ nhàng sang B7.
*   **Sub-task 3.2:** Nếu B7 trả lời `200 OK`, B6 hiện dấu chấm Xanh lá cây (B7 Đang hoạt động) trên Dashboard.
*   **Sub-task 3.3:** Nếu liên tiếp 3 phút không thấy B7 trả lời, B6 lập tức chớp đèn Đỏ trên màn hình của B6 và gửi tin nhắn Telegram cho bộ phận IT: *"Hệ thống báo động B7 đã mất kết nối, yêu cầu đi kiểm tra dây mạng gấp!"*.

---

## 🛠 Task 4: Luật Leo Thang Cảnh Báo (Escalation Policy)
**Vấn đề:** B6 phát hiện thẻ lạ xâm nhập, gửi mức `WARNING` cho B7. Nhưng bác bảo vệ đang ngủ gật nên không bấm nút "Xác nhận đã xử lý" trên màn hình B7. Kẻ gian tha hồ phá hoại.
**Giải pháp:** B6 tự động nâng mức cảnh báo nếu không có ai phản hồi.

*   **Sub-task 4.1:** Yêu cầu B7 mở một API để B6 gọi sang hỏi xem "Cảnh báo ID số 1 đã có ai xử lý chưa?".
*   **Sub-task 4.2:** B6 đếm ngược: Nếu sau 5 phút gửi `WARNING` mà bảo vệ chưa xử lý.
*   **Sub-task 4.3:** B6 tự động nâng cấp (Escalate) sự kiện lên mức `CRITICAL`. Gửi lại lệnh sang B7 yêu cầu: *"Bật còi báo động mức to nhất và gửi SMS gọi trực tiếp cho Trưởng ban An ninh trường!"*.
