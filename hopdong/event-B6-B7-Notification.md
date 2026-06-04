# Event Contract sơ bộ — Core Business (B6) & Notification (B7)

> File này chỉ dùng cho các cặp Queue async ở Lab 02 để ghi nhận thỏa thuận ban đầu. Đặc tả chi tiết bằng AsyncAPI sẽ chuyển sang Lab 03.

## 1. Thông tin dependency

- Dependency số: Cặp 04
- Producer: Core Business (B6)
- Consumer: Notification (B7)
- Cơ chế: Queue async (Kafka/RabbitMQ)
- Event/topic dự kiến: `alert.created`
- Người ghi: Nhóm B6
- Ngày: 26/05/2026

## 2. Mục đích nghiệp vụ

Khi Core Business (B6) phát hiện có đột nhập hoặc cảnh báo an ninh (mở cổng trái phép), B6 sẽ bắn 1 event ra hàng đợi. Notification (B7) sẽ bắt event này để tự động gửi SMS/Email cho đội bảo vệ hoặc sinh viên.

## 3. Event name / topic

| Mục | Giá trị |
|---|---|
| Event name | `core.alert.created` |
| Topic/queue | `campus.alerts` |
| Producer | `core-business` |
| Consumer | `notification-service` |

## 4. Payload tối thiểu

```json
{
  "eventId": "uuid",
  "eventType": "core.alert.created",
  "occurredAt": "2026-05-26T08:30:00Z",
  "correlationId": "uuid-cua-truong-hop-vi-pham",
  "source": "core-business",
  "data": {
    "alertId": "uuid",
    "severity": "HIGH",
    "message": "Phát hiện sinh viên quẹt thẻ khóa",
    "targetUserId": "SV-12345"
  }
}
```

## 5. Ràng buộc cần thống nhất

| Vấn đề | Quyết định tạm thời |
|---|---|
| Event id có bắt buộc không? | Có (Để B7 chống gửi SMS 2 lần) |
| Có cần correlationId không? | Có (Dùng để trace log toàn hệ thống) |
| Có cho phép gửi trùng event không? | Có thể, B7 phải tự check Redis chống spam SMS |
| Retry khi lỗi | Ghi rõ ở Lab 03 |
| Dead-letter queue | Ghi rõ ở Lab 03 |

## 6. Issue chuyển sang Lab 03

1. Template tin nhắn SMS/Email do B6 cấu hình hay B7 cứng trong code?
2. B7 gửi SMS thất bại thì có bắn event `alert.failed` lại cho B6 không?
