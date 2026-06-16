# Ghi Chú Tích Hợp (Integration Notes)

## 1. Môi trường kiểm thử
- Sử dụng **Ngrok** để public cổng `8000` ra ngoài Internet, cho phép B4 và B3 bắn Webhook test chéo một cách an toàn mà không cần config Firewall mạng LAN.
- Khi triển khai thật vào mạng trường (LAN), sử dụng biến `LAN_HOST_IP` trong `.env` thay thế cho Ngrok URL.

## 2. Thông số tích hợp
- **MQTT Broker:** `HiveMQ Cloud` (Sử dụng TLS/SSL Port 8883).
- **MQTT Topics:** `smart-campus/events/sensor` (B1) và `smart-campus/events/camera` (B2).
- **Outbound HTTP Timeout:** Đã set `timeout=5.0s` trong module HTTPX để đề phòng nhóm khác rớt mạng làm nghẽn thread của B6.

## 3. Các vấn đề đã gặp và Khắc phục
- **Sập Service do thiếu DB:** Khắc phục bằng Mock (Mã thẻ `04:A1...` auto được accept).
- **Lỗi MQTT không nhận Data:** Do code ban đầu nhầm topic name của B1, đã xem lại Hợp đồng tích hợp (`B1_IoT_Ingestion_Hop_Dong_Tich_Hop.md`) và sửa thành đúng tên `smart-campus/events/sensor`.
- **405 Method Not Allowed khi B4 gọi `/ai/events`:** Do B4 vô tình dùng phương thức HTTP GET để gửi payload Json. Đã nhắc B4 đổi thành phương thức POST trên Postman.
