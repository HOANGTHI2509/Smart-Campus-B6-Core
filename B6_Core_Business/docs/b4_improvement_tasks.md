# Kế hoạch Nâng cấp Hệ thống: Tối ưu luồng dữ liệu AI Vision (B4)

Tài liệu này liệt kê các thiết kế kiến trúc nâng cao dành riêng cho nhóm B4 (AI Vision), nơi B6 (Core Business) không chỉ thụ động nhận kết quả AI mà còn đóng vai trò kiểm định độ tin cậy và phân tích ngữ cảnh (Contextual Analysis).

---

## 🛠 Task 1: Bộ Lọc Độ Tin Cậy Động (Dynamic Confidence Thresholding)
**Vấn đề:** Trí tuệ nhân tạo (AI) thỉnh thoảng sẽ bị "ảo giác" (nhìn nhầm). Nếu phó mặc hoàn toàn cho AI, còi báo động sẽ rú liên tục vì nhận diện sai ngọn lửa thành ánh sáng mặt trời.
**Giải pháp:** B6 đóng vai trò Thẩm định viên, áp dụng mức điểm chuẩn (Threshold) khác nhau cho từng khu vực.

*   **Sub-task 1.1:** Xây dựng bảng quy tắc bù trừ: `Phòng Server` yêu cầu `confidence > 70%` là hú còi. `Sân cỏ ngoài trời` yêu cầu `confidence > 95%` mới được hú còi (do nhiễu ánh sáng).
*   **Sub-task 1.2:** Cập nhật hàm `receive_vision_alert`: Đọc mảng `detectedObjects`, duyệt từng vật thể và kiểm tra `confidence` của nó so với bảng quy tắc trên.
*   **Sub-task 1.3:** Nếu AI gửi mức độ tin cậy quá thấp (Dưới ngưỡng B6 cho phép), B6 sẽ "Bác bỏ" kết quả đó và coi như là False Alarm (Cảnh báo giả), giữ im lặng không gọi B7.

---

## 🛠 Task 2: Xác Thực Bảo Mật 2 Lớp (2FA - Cross-matching B3 & B4)
**Vấn đề:** Sinh viên A đánh cắp thẻ của Sinh viên B để quét vào thư viện. Cổng an ninh B3 chỉ đọc thẻ nên vẫn mở cửa.
**Giải pháp:** B6 kết hợp thẻ vật lý (B3) và nhận diện khuôn mặt (B4) để bắt quả tang.

*   **Sub-task 2.1:** Khi B3 báo có thẻ quẹt `UID = SV001`. B6 tạm ngưng mở cửa trong 2 giây.
*   **Sub-task 2.2:** B6 yêu cầu Camera của B4 quét khuôn mặt người đang đứng ở cổng. AI B4 trả về kết quả `FaceID = SV009`.
*   **Sub-task 2.3:** B6 tiến hành đối chiếu (Cross-matching): `Thẻ SV001` không khớp với `Mặt SV009`.
*   **Sub-task 2.4:** B6 lập tức từ chối mở cửa, gọi B7 báo động: *"Bắt quả tang sinh viên SV009 xài thẻ ăn cắp của SV001!"*

---

## 🛠 Task 3: Phân Tích Hành Vi Bất Thường (Behavioral Aggregation)
**Vấn đề:** Một kẻ gian không quẹt thẻ, cũng không cầm vũ khí hay gây cháy. Hắn chỉ đứng lượn lờ trước cổng trường suốt 15 phút để rình mò. AI B4 chỉ biết trả về "Đang có người đứng".
**Giải pháp:** B6 xây dựng bộ đếm thời gian phân tích hành vi.

*   **Sub-task 3.1:** B6 lưu lại `cameraId` và `timestamp` mỗi khi B4 báo cáo có người.
*   **Sub-task 3.2:** Nếu B6 nhận thấy tín hiệu "Có người đứng ở Cổng A" liên tục kéo dài hơn 5 phút (Hoặc AI báo cáo đối tượng này vẫn ở trong khung hình).
*   **Sub-task 3.3:** B6 kiểm tra xem trong 5 phút qua có sự kiện quẹt thẻ B3 nào ở Cổng A không. Nếu KHÔNG CÓ ai quẹt thẻ mà vẫn có người đứng lâu như vậy ➡️ Đánh giá là "Hành vi khả nghi (Loitering)" ➡️ Gọi B7 báo cho bảo vệ ra kiểm tra.

---

## 🛠 Task 4: Thu Thập Dữ Liệu "Cảnh Báo Giả" (False Alarm Feedback Loop)
**Vấn đề:** Mô hình AI cần được học lại (Retrain) liên tục nếu nhận diện sai.
**Giải pháp:** B6 cung cấp tính năng "Phản hồi" cho bác bảo vệ.

*   **Sub-task 4.1:** Trên màn hình Dashboard của B6, hiển thị nút "Đây là báo cáo giả" bên cạnh mỗi Alert của AI.
*   **Sub-task 4.2:** Khi bảo vệ xem Camera và bấm vào nút đó, B6 sẽ lưu lại `image_url` của cảnh báo sai.
*   **Sub-task 4.3:** Đóng gói tất cả các ảnh bị sai (False Positives) này và gọi API gửi ngược lại cho nhóm B4 vào cuối ngày để nhóm B4 đưa vào Dataset huấn luyện lại mô hình AI cho xịn hơn.
