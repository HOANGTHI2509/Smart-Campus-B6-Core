# B6 Core Architecture One-Pager

## 1. Giới thiệu tổng quan
Hệ thống **B6 Core Business** đóng vai trò làm trung tâm điều phối (Orchestration) trong mô hình Smart Campus. Dựa trên Clean Architecture kết hợp Event-Driven Design, B6 liên kết các hệ thống phần cứng/camera và hệ thống thông báo/quản trị.

## 2. Các thành phần chính (Components)
1. **MQTT Client (Real-time Ingestion):** Khởi chạy ngầm (Non-blocking Thread) bằng thư viện `paho-mqtt` kết nối với HiveMQ Cloud. Đảm nhiệm thu thập tín hiệu sensor 24/7 từ B1/B2.
2. **FastAPI Gateway (REST Inbound):** Phục vụ các Webhook cho B3 (Cổng vật lý) và B4 (AI Vision) qua giao thức HTTP(s).
3. **Policy Engine (Xử lý nghiệp vụ):** Trung tâm đối chiếu logic. Quyết định khi nào thì gọi Outbound sang các nhóm Notification/Analytics.
4. **Outbound Service (REST Outbound):** Quản lý kết nối mạng LAN/Ngrok tới các dịch vụ B3, B5, B7, hỗ trợ cơ chế timeout để chống sập dây chuyền (Cascading Failure).
5. **In-Memory Logger:** Lưu trữ trạng thái Real-time phục vụ vẽ giao diện Dashboard giám sát.

## 3. Kiến trúc Triển khai (Deployment)
- Chạy trên container `b6-core-api` quản lý bởi Docker Compose.
- Sử dụng Ngrok Tunnels để vượt qua mạng NAT (NAT Traversal), cung cấp Public URL cho các nhóm kết nối dễ dàng thay vì phụ thuộc LAN IP.

## 4. Lý do thiết kế (Design Decisions)
- **Single Responsibility:** B6 không tự đánh giá rủi ro (Nhiệt độ bao nhiêu là cháy?), việc này đẩy về B1. B6 chỉ quyết định: "Khi B1 hô cháy thì mình phải làm gì?".
- **Bất đồng bộ (Async/Await):** Các tác vụ gọi Outbound sang B7, B3 được sử dụng HTTPX AsyncClient để tránh nghẽn thread chính của Web Server.
