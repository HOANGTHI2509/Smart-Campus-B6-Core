# Changelog - Lịch sử cập nhật API (Nhóm B6)

Tất cả những thay đổi về API, Payload và cấu trúc giao tiếp có ảnh hưởng đến các nhóm khác (Breaking Changes) sẽ được ghi chú tại đây theo đúng yêu cầu của hệ thống Microservices.

## [1.1.0] - 2026-06-19
### Thay đổi (Changed)
- **(B3 - Access Gate):** Cập nhật logic xử lý của API `POST /api/v1/events/access`. 
  - Thêm luật cấm quẹt đêm (22h-6h) và luật chống quẹt liên tục (Rate Limit / Anti-passback 5 giây).
  - Kết quả trả về (Response) có thể trả thêm các trường hợp `{"allowed": false, "reason": "Rate limit exceeded. Please wait."}` hoặc `"reason": "Access denied. Outside allowed hours."`. Đã yêu cầu nhóm B3 cập nhật màn hình hiển thị LCD.
- **(B7 - Notification):** Chuẩn hóa cấu trúc JSON Payload gọi sang API `POST /notify/send` của nhóm B7.
  - Payload mới: `{"alert_id": "ALT-XXX", "type": "unauthorized_access", "severity": "high", "message": "..."}`. Đã thông báo nhóm B7 cập nhật Schema hứng data.

## [1.0.3] - 2026-06-17
### Thêm mới & Cải thiện (Added & Improved)
- Hoàn thiện toàn bộ Microservice B6: Bổ sung tài liệu API, giao thức SSE (Server-Sent Events) đẩy dữ liệu real-time.
- Thêm Endpoint `GET /health` phục vụ Healthcheck cho hệ thống.
- Chuyển đổi cấu trúc mạng sang Radmin VPN để kết nối nội bộ với các nhóm khác.
- Cập nhật bộ kịch bản kiểm thử Postman.

## [1.0.2] - 2026-06-16
### Thêm mới (Added)
- Tích hợp thành công thư viện `paho-mqtt` để hứng luồng dữ liệu IoT.
- Viết tính năng tự động gọi cảnh báo sang nhóm B7 khi phát hiện rủi ro.

## [1.0.1] - 2026-06-13
### Thêm mới (Added)
- Thiết lập các Model Database và ẩn các thông tin bí mật (Secrets) vào file `.env`.
- Bổ sung các Outbound API client để chuẩn bị giao tiếp với nhóm B3 và B7.
- Xây dựng logic xác thực quyền ra vào (Access logic) cơ bản.

## [1.0.0] - 2026-05-12
### Khởi tạo (Init)
- Khởi tạo project B6 Core Business.
- Setup FastAPI, môi trường Docker, và cấu hình Database.
