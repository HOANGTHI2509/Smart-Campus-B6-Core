# Event Contract sơ bộ — Core Business (B6) & Analytics (B5)

> File này chỉ dùng cho các cặp Queue async ở Lab 02 để ghi nhận thỏa thuận ban đầu. Đặc tả chi tiết bằng AsyncAPI sẽ chuyển sang Lab 03.

## 1. Thông tin dependency

- Dependency số: Cặp 08
- Producer: Core Business (B6)
- Consumer: Analytics (B5)
- Cơ chế: Queue async (Kafka/Data Pipeline)
- Event/topic dự kiến: `core.business.log`
- Người ghi: Nhóm B6
- Ngày: 26/05/2026

## 2. Mục đích nghiệp vụ

Mọi hành động quan trọng diễn ra trong hệ thống lõi (người dùng qua cổng, cảnh báo được tạo ra, thiết bị hỏng) đều được B6 đóng gói thành event và vứt vào Data Lake/Kafka. Nhóm Analytics (B5) sẽ hút các event này về để tổng hợp báo cáo KPI và vẽ biểu đồ Dashboard cho Ban giám hiệu.

## 3. Event name / topic

| Mục | Giá trị |
|---|---|
| Event name | `core.audit.event` |
| Topic/queue | `campus.audit.logs` |
| Producer | `core-business` |
| Consumer | `analytics-service` |

## 4. Payload tối thiểu

```json
{
  "eventId": "uuid",
  "eventType": "core.audit.event",
  "occurredAt": "2026-05-26T08:30:00Z",
  "correlationId": "uuid-cua-hanh-dong",
  "source": "core-business",
  "data": {
    "actionType": "ACCESS_GRANTED",
    "actorId": "SV-12345",
    "resourceId": "GATE-01",
    "status": "SUCCESS",
    "metadata": {
      "confidence": 0.95
    }
  }
}
```

## 5. Ràng buộc cần thống nhất

| Vấn đề | Quyết định tạm thời |
|---|---|
| Event id có bắt buộc không? | Có (Dùng để de-duplicate trên kho dữ liệu) |
| Có cần correlationId không? | Có (Dùng để ghép nối các thao tác vào 1 luồng) |
| Có cho phép gửi trùng event không? | Có, B5 (Data Warehouse) tự merge theo `eventId` |
| Retry khi lỗi | Ghi rõ ở Lab 03 |
| Dead-letter queue | Ghi rõ ở Lab 03 |

## 6. Issue chuyển sang Lab 03

1. Định dạng dữ liệu (JSON hay Avro/Protobuf)? Analytics thường thích Avro vì Schema Registry.
2. Việc lưu trữ dữ liệu PII (như tên, mã số sinh viên) có cần B6 ẩn danh (masking) trước khi đẩy sang B5 không?
