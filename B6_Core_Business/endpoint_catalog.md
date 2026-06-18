# Endpoint Catalog (B6 Core Business)

Tài liệu liệt kê các API Inbound (do B6 cung cấp) và Outbound (B6 gọi đi).

## 1. Inbound APIs (Nhận Request từ nhóm khác)

### 1.1 Kiểm tra trạng thái hệ thống
- **Endpoint:** `GET /health`
- **Mô tả:** API cơ bản dùng để Ngrok và Docker kiểm tra tình trạng sống/chết của Service B6.
- **Response (200 OK):**
```json
{
  "status": "ok",
  "service": "b6-core-business",
  "version": "1.0.0"
}
```

### 1.2 Webhook nhận báo động từ AI Vision (B4)
- **Endpoint:** `POST /ai/events`
- **Mô tả:** Nhận phân tích nguy hiểm (cháy, bạo lực) từ B4.
- **Request Body (JSON):**
```json
{
  "detectionId": "string",
  "cameraId": "string",
  "detectionType": "OBJECT",
  "riskLevel": "CRITICAL",
  "timestamp": "ISO-8601"
}
```
- **Response (200 OK):** `{"message": "Alert received and processed successfully by Core B6"}`

### 1.3 Webhook nhận quẹt thẻ từ Access Gate (B3)
- **Endpoint:** `POST /access/check`
- **Mô tả:** Khi có sinh viên quẹt thẻ, B3 bắn mã thẻ (UID) sang đây để xin phép mở cửa.
- **Request Body:**
```json
{
  "gateId": "GATE_A",
  "uid": "04:A1:XX:YY",
  "timestamp": "ISO-8601"
}
```
- **Response (200 OK):** `{"allowed": true, "reason": "Access granted", "studentId": "SV001"}`

## 2. Outbound APIs (B6 gọi sang nhóm khác)

### 2.1 Kích hoạt chuông báo cháy (B7)
- **Endpoint:** `POST {B7_URL}/notify/send`
- **Trường hợp gọi:** Khi B1 (IoT) hoặc B4 (AI) gửi tín hiệu cháy nổ.

### 2.2 Ra lệnh mở cổng khẩn cấp (B3)
- **Endpoint:** `POST {B3_URL}/gate/command`
- **Trường hợp gọi:** Khi có cháy (CRITICAL), B6 tự động ra lệnh mở cổng để sinh viên thoát hiểm.
- **Body gửi đi:** `{"command": "OPEN", "uid": "EMERGENCY"}`

### 2.3 Xuất Log cho Analytics (B5)
- **Endpoint:** `POST {B5_URL}/analytics/export`
- **Trường hợp gọi:** Theo định kỳ hoặc khi có yêu cầu đồng bộ.
