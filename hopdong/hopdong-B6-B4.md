# BIÊN BẢN CHỐT HỢP ĐỒNG API — CORE BUSINESS (B6) & AI VISION (B4)

Dựa trên quá trình đàm phán, hai nhóm B6 và B4 đã đi đến thống nhất các giải pháp kiến trúc và thông số kỹ thuật cuối cùng. Tài liệu này đóng vai trò là cơ sở để cả hai bên triển khai hệ thống và cập nhật `openapi.yaml`.

---

## 1. Dữ liệu Đầu vào (Payload)
- **Thống nhất:** B6 gửi `imageRef` (URL hoặc đường dẫn S3).
- **Lý do:** B4 cần ảnh gốc để tự trích xuất vector khuôn mặt (faceEmbedding), tránh rủi ro lệch phiên bản thư viện trích xuất giữa hai hệ thống.

## 2. Ngưỡng Chính Xác (Confidence Threshold)
- **Thống nhất:** Ngưỡng tự động đánh dấu khớp (`faceMatched: true`) được chốt cứng ở mức **90%** (0.90).
- **Xử lý ngoại lệ (< 90%):** B4 vẫn trả về `HTTP 200 OK` nhưng gán `faceMatched: false` và `matchedPersonId: null`. B6 sẽ đọc tỷ lệ % thực tế để có hành động nghiệp vụ tương ứng (ví dụ: còi báo nhẹ).

## 3. Xử lý Ảnh Mờ / Không Thấy Mặt
- **Thống nhất:** B4 trả về `HTTP 200 OK` kèm `status: "low_confidence"` hoặc `"no_face_detected"`.
- **Lý do:** Đây là kết quả nghiệp vụ hợp lệ của AI, không phải lỗi hệ thống. Mã `422` chỉ được dùng khi B6 truyền dữ liệu sai định dạng (ví dụ: URL hỏng).

## 4. Xử lý Nhiều Khuôn Mặt (Multiple Faces)
- **Thống nhất:** API đồng bộ (REST) chỉ trả về duy nhất **01 khuôn mặt to nhất/gần nhất** để B6 xử lý nhanh tiến trình mở cổng.
- **Chống bám đuôi (Tailgating):** AI của B4 sẽ đếm mặt ngầm, nếu có từ 2 mặt trở lên, B4 sẽ bắn một luồng Webhook bất đồng bộ (Tailgating Alert) sang cho B6 để cảnh báo bảo vệ, không làm nghẽn luồng mở cổng chính.

## 5. Hiệu Năng và Độ Trễ (SLA & Timeout)
- **SLA Cam kết:** Thời gian xử lý trung bình < 300ms, tối đa **800ms**.
- **Xử lý Timeout:** B6 set timeout = 1 giây. Nếu B6 ngắt kết nối, server B4 sẽ bắt sự kiện đóng kết nối và ngay lập tức hủy luồng GPU (abort inference) để giải phóng RAM, chống rò rỉ tài nguyên.

## 6. Chống Giả Mạo (Liveness Detection)
- **Thống nhất:** B4 có hỗ trợ Liveness Detection và thêm trường `isLive: boolean` vào OpenAPI.
- **Hành động:** Nếu `isLive: false` (phát hiện giả mạo qua màn hình điện thoại), B6 sẽ từ chối mở cổng và báo động.

## 7. Chống Quá Tải (Rate Limiting)
- **Ngưỡng tải:** B4 chịu tải tối đa **50 RPS** (Request/Giây).
- **Phản hồi quá tải:** Vượt quá 50 RPS, B4 trả về lỗi `HTTP 429 Too Many Requests` (dạng Problem Details) kèm Header `Retry-After`.
- **Fail-safe của B6:** Khi nhận mã 429, B6 tự động bỏ qua xác thực khuôn mặt, cho phép sinh viên qua cổng chỉ bằng thẻ từ để giải tỏa ách tắc.

---
**Trạng thái:** ĐÃ CHỐT KÝ 🤝
