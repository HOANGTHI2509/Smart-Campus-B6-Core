# Kế Hoạch Tích Hợp & Phân Công Nhiệm Vụ Nhóm B6 (Core Business)

Dự án phát triển bằng **Python (FastAPI)**. Dưới đây là kế hoạch chi tiết chia cho 3 thành viên và lộ trình tích hợp ưu tiên để đảm bảo buổi Demo (Buổi 6) thành công.

---

## 🌟 PHẦN 1: LỘ TRÌNH ƯU TIÊN TÍCH HỢP

Nhóm cần tiến hành tích hợp theo đúng thứ tự từ dễ đến khó để không bị block tiến độ:

1. **Ưu tiên 1: Lập trình nội bộ (DB + Master Data)** 
   - *Mục tiêu:* Tự nhóm dựng xong FastAPI, kết nối Database và nạp 2 file CSV vào. Không phụ thuộc vào ai.
2. **Ưu tiên 2: Kết nối Nhóm IoT (B1) và Camera (B2)** 
   - *Hình thức:* MQTT (Qua Internet/HiveMQ).
   - *Lý do:* Rất dễ test. Chỉ cần có mạng Internet, code chạy là nhận được data ngay. Giúp hệ thống có luồng dữ liệu liên tục để test các Policy (Cảnh báo).
3. **Ưu tiên 3: Kết nối Nhóm AI Vision (B4) - ĐỐI TÁC QUAN TRỌNG NHẤT**
   - *Hình thức:* HTTP/REST API (Qua mạng LAN Hotspot).
   - *Lý do:* Rất dễ lỗi mạng. Cần bắt chung Wi-Fi, kiểm tra IP liên tục, mở/tắt Firewall. Cần đảm bảo endpoint `/ai/events` và `/health` của B6 hoạt động để B4 gọi vào.
4. **Ưu tiên 4: Kết nối Nhóm Access Gate (B3)**
   - *Hình thức:* HTTP/REST API (Inbound/Outbound).
   - *Lý do:* Logic đơn giản, nhận UID từ B3 rồi gọi lệnh mở cửa lại cho B3.
5. **Ưu tiên 5: Nhóm Notification (B7) và Analytics (B5)**
   - *Hình thức:* HTTP Outbound (B6 chủ động gọi đi).
   - *Lý do:* Đơn giản nhất. Chỉ cần xin IP của họ và dùng `httpx` POST JSON sang là xong, không cần cấu hình Firewall chiều vào.

---

## 👨‍💻 PHẦN 2: BẢNG PHÂN CÔNG CHI TIẾT (3 THÀNH VIÊN)

### 👤 Thành viên 1: Nhóm Trưởng (Leader) - Chuyên trách Core API & Mạng (LAN/REST)
*Chịu trách nhiệm kiến trúc lõi (FastAPI) và điều phối mạng LAN rủi ro cao.*

- [x] **Task 1.1:** Khởi tạo project FastAPI, thiết lập cấu trúc thư mục, viết `Dockerfile` và `docker-compose.yml` (Chạy tất cả trên 1 máy ảo).
- [x] **Task 1.2:** Thiết lập file `.env` chứa địa chỉ IP của các nhóm khác. Đảm bảo app FastAPI cấu hình host `0.0.0.0:8000`.
- [x] **Task 1.3:** Viết API `GET /health` (bắt buộc theo chuẩn của thầy).
- [x] **Task 1.4:** Viết API Inbound Router `POST /ai/events` (Webhook để B4 đẩy báo động khói/cháy).
- [x] **Task 1.5:** Viết API Inbound Router `POST /access/check` (Nhận UID từ B3 xin mở cổng).
- [x] **Task 1.6:** Viết các class Outbound Client (dùng thư viện `httpx`) để chủ động gọi sang B4 (Face Match), gọi B7 (Báo động), gọi B3 (Ra lệnh mở cổng).
- [ ] **Hỗ trợ Demo:** Quản lý IP máy cá nhân (Hotspot), tắt/mở Windows Firewall để các nhóm khác có thể gọi vào.

### 👤 Thành viên 2: Kỹ Sư Dữ Liệu Thời Gian Thực (Chuyên trách MQTT)
*Chịu trách nhiệm kết nối Internet lấy dữ liệu từ các luồng Streaming.*

- [x] **Task 2.1:** Dùng thư viện Python `paho-mqtt` thiết lập kết nối với HiveMQ Cloud bằng Account IoT cấp (Đọc từ file `.env`).
- [x] **Task 2.2:** Viết hàm Subscribe lắng nghe topic `smart-campus/events/sensor` của nhóm B1 (IoT).
- [x] **Task 2.3:** Viết Business Logic Engine (Xử lý Policy): Phân tích cú pháp JSON từ IoT, check ngưỡng nhiệt độ, khói. Nếu nguy hiểm -> Gọi module Outbound của Leader để bắn lệnh sang nhóm B7.
- [x] **Task 2.4:** Subscribe lắng nghe topic `smart-campus/events/camera` của nhóm B2. Bắt các event phát hiện chuyển động.
- [x] **Yêu cầu Minh chứng:** Cài đặt log xịn (ví dụ: thư viện `loguru`). Mỗi khi MQTT nhận tin nhắn, in JSON có định dạng màu mè ra màn hình console để show cho giảng viên chấm.

### 👤 Thành viên 3: Kỹ Sư Dữ Liệu & Master Data (Chuyên trách Database)
*Chịu trách nhiệm xây dựng nền móng dữ liệu (Làm độc lập, có thể code ngay lập tức).*

- [ ] **Task 3.1:** Thiết lập Database ( PostgreSQL). Dùng `SQLAlchemy` khai báo các bảng: `Users`, `Devices`, `AccessLogs`, `Rules`.
- [ ] **Task 3.2:** Viết đoạn script Python (dùng thư viện `pandas` hoặc đọc file `.csv` thuần) để tự động import 2 file của thầy vào Database khi chạy app:
   - Import `Acessgate_uid_whitelist.csv` -> Bảng `Users`.
   - Import `IoT_device_registry.csv` -> Bảng `Devices`.
- [ ] **Task 3.3:** Cung cấp 2 hàm truy vấn (Queries) cho Leader và Thành viên 2 dùng:
   - `def get_student_by_uid(uid: str):` -> Phục vụ lúc B3 gọi API quẹt thẻ.
   - `def get_device_location(device_id: str):` -> Phục vụ lúc MQTT nhận event cảm biến, cần biết vị trí báo cháy nằm ở phòng nào.
- [ ] **Task 3.4 (Backup):** Viết sẵn vài hàm sinh Mock Data (Dữ liệu giả lập) vào DB phòng trường hợp lúc Demo các nhóm khác bị sập mạng thì B6 vẫn có data nội bộ để chạy.
