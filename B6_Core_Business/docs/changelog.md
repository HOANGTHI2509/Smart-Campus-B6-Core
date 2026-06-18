# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Tích hợp MQTT kết nối HiveMQ Cloud nhận dữ liệu B1/B2.
- Dashboard Web UI Real-time (`/dashboard`) hiển thị log JSON.
- REST API `POST /access/check` cấp quyền mở cổng bằng Mock Logic.
- REST API `POST /ai/events` xử lý sự kiện báo cháy từ AI Vision B4.
- Outbound Webhooks (Sử dụng `httpx` async) ra lệnh cho B7 (Notification) và B3 (Access Gate).
- `.env` support với tính năng tự động chuyển đổi giữa Ngrok URL và mạng LAN.

### Changed
- Refactor cấu trúc sang chuẩn Microservices (bỏ hard-code IP tĩnh).
- Áp dụng nguyên tắc Single Responsibility: B6 tin tưởng 100% vào quyết định rủi ro của B1 thay vì tự check lại ngưỡng cảm biến.

### Fixed
- Bị crash Server khi thiếu file Database bằng cách thay thế DB logic thành In-Memory Mock.
- Khắc phục lỗi `ModuleNotFoundError: No module named 'app.scripts.import_data'`.
- Khắc phục sai MQTT Topic (`smart-campus/sensors/#` -> `smart-campus/events/sensor`) theo đúng hợp đồng B1.
