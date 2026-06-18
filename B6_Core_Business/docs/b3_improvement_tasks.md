# Kế hoạch Nâng cấp Hệ thống: Tối ưu luồng dữ liệu Cổng An Ninh (B3)

Tài liệu này định hướng phát triển các tính năng bảo mật nâng cao mà nhóm Core Business (B6) có thể xử lý đối với dữ liệu quẹt thẻ từ Cổng An Ninh (B3).

---

## 🛠 Task 1: Chống Quay Vòng Thẻ (Anti-Passback System)
**Vấn đề:** Sinh viên A quẹt thẻ đi qua cổng (IN), sau đó lén luồn thẻ qua khe hở đưa cho sinh viên B quẹt tiếp (IN) để trốn vé hoặc điểm danh hộ.
**Giải pháp:** B6 lưu trạng thái vị trí (State Tracking) của từng chiếc thẻ.

*   **Sub-task 1.1:** Xây dựng một bảng/biến lưu trạng thái hiện tại của từng thẻ: `Thẻ 04:A1` đang ở `Trong trường` hay `Ngoài trường`.
*   **Sub-task 1.2:** Cập nhật logic trong `app/main.py`: Khi B3 báo cáo Thẻ 04:A1 vừa quẹt đi vào (IN), B6 sẽ check trạng thái.
*   **Sub-task 1.3:** Nếu trạng thái thẻ đang là `Trong trường` mà lại có sự kiện quẹt vào (IN) một lần nữa ➡️ Xác nhận vi phạm quay vòng thẻ (Anti-passback Violation) ➡️ Từ chối (Nếu B3 cho phép) và cảnh báo sang B7 để bảo vệ tóm cổ tại trận!

---

## 🛠 Task 2: Phân Quyền Truy Cập Động (Dynamic Access Control)
**Vấn đề:** B3 tự quyết định mở cửa mà không biết sinh viên đó có học môn đó không. Một sinh viên kinh tế quẹt thẻ vào phòng Lab Server IT thì rất vô lý.
**Giải pháp:** B6 làm chủ cơ sở dữ liệu phân quyền. 

*   **Sub-task 2.1:** Tạo Cơ sở dữ liệu phân quyền: `Sinh viên A` chỉ được vào `Thư viện` và `Giảng đường`. `Giáo sư B` được vào `Phòng Server`.
*   **Sub-task 2.2:** Mặc dù B3 báo cáo đã mở cửa, B6 vẫn kiểm tra chéo (Cross-check) với CSDL phân quyền.
*   **Sub-task 2.3:** Nếu sinh viên A lẻn vào phòng Server ➡️ Hành động hợp lệ về mặt thẻ vật lý nhưng SAI về mặt Quyền Truy Cập ➡️ B6 gửi cảnh báo mức HIGH (Truy cập khu vực hạn chế) cho B7.

---

## 🛠 Task 3: Kích Hoạt Sơ Tán Khẩn Cấp (Emergency Evacuation Override)
**Vấn đề:** B3 hiện tại đang tự hành, không cho phép điều khiển từ xa. Nếu cháy nhà, sinh viên hoảng loạn không tìm thấy thẻ thì sẽ kẹt trong trường.
**Giải pháp:** B6 dùng "Quyền lực" của Core Business ép B3 phải mở API khẩn cấp.

*   **Sub-task 3.1:** Bổ sung vào Hợp đồng API bắt buộc B3 cung cấp 1 endpoint: `POST /gate/emergency-open`.
*   **Sub-task 3.2:** B6 kết nối với B1 (Cảm biến nhiệt). Khi B1 báo cháy (is_emergency = True).
*   **Sub-task 3.3:** B6 không chỉ gọi B7 hú còi, mà còn song song gọi thẳng vào API `/gate/emergency-open` của B3 để "Hack" mô tơ, ép tất cả các cổng phải mở toang (Fail-Safe Mode) phục vụ sơ tán.

---

## 🛠 Task 4: Làm Sạch và Chuyển Tiếp Dữ Liệu (Data Pipeline to B5)
**Vấn đề:** B6 nhận hàng ngàn lượt quẹt thẻ mỗi sáng, nếu cứ lưu mãi trong Database của B6 thì sẽ nặng máy.
**Giải pháp:** B6 đóng vai trò Data Pipeline, đóng gói dữ liệu đẩy sang hệ thống Thống kê (Analytics - B5).

*   **Sub-task 4.1:** Gom nhóm (Batching) các event quẹt thẻ hợp lệ trong vòng 1 phút (ví dụ 100 người quẹt thẻ vào trường).
*   **Sub-task 4.2:** Nén cục dữ liệu 100 người đó lại và gọi API ném sang hệ thống B5 (Analytics).
*   **Sub-task 4.3:** B5 sẽ dùng dữ liệu đó để vẽ biểu đồ "Điểm danh", "Giờ cao điểm kẹt xe ở cổng trường", giúp B6 giảm tải dung lượng lưu trữ.
