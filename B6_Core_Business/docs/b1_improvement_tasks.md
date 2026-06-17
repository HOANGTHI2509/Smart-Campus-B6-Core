# Kế hoạch Nâng cấp Hệ thống: Tối ưu luồng dữ liệu IoT (B1)

Tài liệu này chia nhỏ các tính năng định hướng nâng cao chất lượng kiến trúc Core Business (B6) khi xử lý luồng dữ liệu khổng lồ từ hệ thống IoT (B1). Phân công công việc theo từng Task nhỏ để dễ dàng quản lý.

---

## 🛠 Task 1: Thuật toán Chống Spam (Debouncing & Rate Limiting)
**Vấn đề:** B1 có thể gửi 10 cảnh báo cháy trong 1 giây. Việc gọi sang B7 10 lần liên tục sẽ làm sập mạng hoặc gây phiền nhiễu không cần thiết.
**Giải pháp:** B6 cần ghi nhớ thời gian gửi cảnh báo gần nhất và tạo "thời gian trễ" (Cooldown) trước khi gửi cảnh báo tiếp theo.

*   **Sub-task 1.1:** Tạo biến (hoặc Redis cache) lưu trữ trạng thái `last_alert_time` cho từng `device_id`.
*   **Sub-task 1.2:** Cập nhật hàm `handle_sensor_data` trong `mqtt_client.py`: Kiểm tra nếu `(CurrentTime - last_alert_time) < 60 giây`, bỏ qua việc gọi API B7, chỉ ghi log.
*   **Sub-task 1.3:** Đảm bảo vẫn lưu vào DB/Log để không mất dữ liệu lịch sử, chỉ cắt luồng gọi báo động (Outbound).

---

## 🛠 Task 2: Xây dựng Bộ lọc Luật Nghiệp vụ (Threshold Rule Engine)
**Vấn đề:** B6 đang phụ thuộc hoàn toàn vào trạng thái `status="danger"` của B1. Điều này làm mất vai trò "Core Business" của B6.
**Giải pháp:** B6 tự định nghĩa các ngưỡng (thresholds) báo động bằng file cấu hình thay vì cứng nhắc.

*   **Sub-task 2.1:** Tạo file cấu hình `rules.json` hoặc lưu vào DB các ngưỡng an toàn:
    *   `Max_Temperature: 50.0`
    *   `Max_Smoke: 1.0`
*   **Sub-task 2.2:** Cập nhật logic: Đọc trực tiếp biến `temperature_c` và `smoke_ppm` từ payload JSON của B1. So sánh với cấu hình trên B6.
*   **Sub-task 2.3:** Nếu các chỉ số vượt ngưỡng, tự động chèn cờ `is_emergency = True` và gọi báo cháy, bất chấp biến `status` của B1 là gì.

---

## 🛠 Task 3: Tích hợp Cơ sở dữ liệu (Database Persistence)
**Vấn đề:** Nhật ký hệ thống (Logs) đang lưu trên RAM (in-memory), sẽ mất trắng khi container khởi động lại. Cần lưu dữ liệu môi trường để có thể xuất báo cáo.
**Giải pháp:** Kết nối với cơ sở dữ liệu quan hệ (PostgreSQL / SQLite) hoặc NoSQL (MongoDB).

*   **Sub-task 3.1:** Cài đặt thư viện ORM (như `SQLAlchemy` hoặc `Motor`).
*   **Sub-task 3.2:** Khởi tạo Table/Collection `EnvironmentLogs` chứa các cột: `timestamp`, `device_id`, `temperature`, `humidity`, `co2`, v.v.
*   **Sub-task 3.3:** Nhúng lệnh `db.insert()` vào cuối hàm `handle_sensor_data` để lưu trữ sau khi đã xử lý xong.

---

## 🛠 Task 4: Tính năng "Trùm cuối" - Phân tích chéo (Multi-modal Sensor Fusion)
**Vấn đề:** Ngăn chặn tình huống sinh viên trêu đùa bằng cách hơ bật lửa vào cảm biến B1, gây ra tình trạng "báo cháy giả".
**Giải pháp:** B6 kết hợp sức mạnh của 2 nguồn dữ liệu: Cảm biến (B1) và Trí tuệ nhân tạo (B4).

*   **Sub-task 4.1:** Xây dựng tính năng "Giữ lại cảnh báo": Khi B1 báo cháy, đặt một cờ `pending_fire_alert` cho phòng (ví dụ: Lab A101) và đếm ngược 5 giây.
*   **Sub-task 4.2:** Trong 5 giây đó, hệ thống chờ đợi tin nhắn Webhook từ nhóm B4 (AI Vision). Nếu B4 cũng báo cáo có `FIRE` ở cùng khu vực `Lab A101`.
*   **Sub-task 4.3:** Viết logic ra quyết định (Decision Logic):
    *   `B1 (Danger) + B4 (FIRE)` ➡️ Xác nhận hỏa hoạn thực sự ➡️ Báo động CRITICAL.
    *   `B1 (Danger) + B4 (Normal)` ➡️ Có thể là báo giả/lỗi cảm biến ➡️ Gửi thông báo WARNING điều phối bảo vệ đi kiểm tra.
