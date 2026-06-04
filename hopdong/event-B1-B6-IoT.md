# Event Contract sơ bộ — IoT Ingestion (B1) & Core Business (B6)

> File này chỉ dùng cho các cặp Queue async ở Lab 02 để ghi nhận thỏa thuận ban đầu. Đặc tả chi tiết bằng AsyncAPI sẽ chuyển sang Lab 03.

## 1. Thông tin dependency

- Dependency số: Cặp 05
- Producer: IoT Ingestion (B1)
- Consumer: Core Business (B6)
- Cơ chế: Queue async (Kafka / MQTT) - (Tạm dùng Mock REST `POST /events/sensor` ở Lab 02)
- Event/topic dự kiến: `sensor.events`
- Người ghi: Nhóm B6
- Ngày: 26/05/2026

## 2. Mục đích nghiệp vụ

Các cảm biến của trường đẩy dữ liệu thô về cụm IoT (B1). B1 xử lý và bắn event sang Queue. B6 sẽ hứng các event này để ra quyết định an ninh (đặc biệt quan tâm đến event báo cháy, vượt ngưỡng nhiệt độ).

## 3. Event name / topic

| Mục | Giá trị |
|---|---|
| Event name | `sensor.reading.created`, `sensor.threshold.exceeded`, `device.status.changed` |
| Topic/queue | `campus.telemetry` |
| Producer | `iot-ingestion` |
| Consumer | `core-business` |

## 4. Payload tối thiểu (Đã đồng bộ với OpenAPI của B1)

B1 đã sử dụng `oneOf` discriminator rất chuẩn xác. Dưới đây là ví dụ payload cho sự kiện khẩn cấp (Vượt ngưỡng cháy):

```json
{
  "eventType": "sensor.threshold.exceeded",
  "eventId": "0196fb3d-4ad7-7d1e-9f49-5d5148d2b444",
  "correlationId": "0196fb3d-4ad7-7d1e-9f49-5d5148d2babc",
  "deviceId": "SENSOR-002",
  "locationId": "LAB-01",
  "sensorType": "smoke",
  "value": 88.2,
  "unit": "ppm",
  "threshold": 70,
  "severity": "HIGH",
  "timestamp": "2026-05-19T04:34:00Z"
}
```

## 5. Ràng buộc cần thống nhất

| Vấn đề | Quyết định tạm thời |
|---|---|
| Event id có bắt buộc không? | Có |
| Có cần correlationId không? | Có (B1 đã đưa vào schema bắt buộc) |
| Có cho phép gửi trùng event không? | Có, B6 sẽ dùng kỹ thuật trượt (Sliding Window) để tính toán |
| Xử lý khi thiết bị offline | B1 sẽ bắn event `device.status.changed` (OFFLINE) |

## 6. Issue chuyển sang Lab 03

1. Tần suất (Sampling rate) của event `sensor.reading.created` là bao lâu? Nếu quá nhiều sẽ làm nghẽn B6.
2. B6 có thể subscribe riêng rẽ chỉ lấy `sensor.threshold.exceeded` không hay phải nhận toàn bộ event và tự lọc?
