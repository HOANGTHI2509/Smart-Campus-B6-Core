# Smart Campus - B6 Core Business Service

## 1. Tên service
**B6 - Core Business (API Gateway & Policy Engine)**

## 2. Vai trò của service trong hệ thống
B6 đóng vai trò là "Bộ Não" (Core Business) của toàn bộ hệ thống Smart Campus. Service này có các nhiệm vụ chính:
- Nhận luồng dữ liệu thời gian thực (MQTT) từ các cảm biến (B1) và camera (B2).
- Hứng các cảnh báo an ninh (Webhook) từ hệ thống AI Vision (B4).
- Tiếp nhận yêu cầu mở cổng từ Access Gate (B3) và đối chiếu với Cơ sở dữ liệu (Master Data) để cấp quyền.
- Điều phối hành động (Orchestration): Ra lệnh báo động cho nhóm Notification (B7) và mở cổng khẩn cấp (B3) khi phát hiện hỏa hoạn.

## 3. Thành viên nhóm
- **Thành viên 1:** Nhóm trưởng (Core API & Mạng LAN/REST).
- **Thành viên 2:** Kỹ sư Dữ liệu Thời gian thực (Chuyên trách MQTT).
- **Thành viên 3:** Kỹ sư Dữ liệu & Master Data (Chuyên trách Database & Mock Data).

## 4. Công nghệ sử dụng
- **Backend Framework:** FastAPI (Python 3.11)
- **Real-time Messaging:** Paho MQTT (kết nối HiveMQ Cloud)
- **Containerization:** Docker & Docker Compose
- **Giao tiếp API:** HTTPX (Asynchronous HTTP client)
- **Web UI:** HTML/CSS/JS (Vanilla) phục vụ Dashboard giám sát.

## 5. Cách chạy local
Đảm bảo bạn đã cài đặt Python 3.11+.
```bash
# 1. Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Tạo file .env từ .env.example
cp .env.example .env
# Chỉnh sửa file .env với cấu hình MQTT và Ngrok tương ứng

# 4. Chạy Server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 6. Cách chạy bằng Docker
```bash
# Chạy Docker Compose (sẽ tự động build image và map port 8000)
docker-compose up --build -d

# Xem log để kiểm tra kết nối MQTT
docker-compose logs -f
```

## 7. Danh sách endpoint chính
- `GET /health` : Kiểm tra trạng thái sức khỏe của Service (Dùng để test Ngrok/LAN).
- `GET /dashboard` : Mở giao diện Giám sát trực quan (UI).
- `POST /access/check` : API nhận sự kiện quẹt thẻ từ nhóm B3.
- `POST /ai/events` : API nhận cảnh báo phát hiện cháy/người lạ từ nhóm B4.

## 8. Service upstream/downstream
- **Upstream (Gửi dữ liệu cho B6):** 
  - B1 (IoT Ingestion) qua MQTT.
  - B2 (Camera Streaming) qua MQTT.
  - B4 (AI Vision) qua HTTP POST.
  - B3 (Access Gate) qua HTTP POST.
- **Downstream (B6 gọi tới):**
  - B7 (Notification) qua HTTP POST để hú còi.
  - B3 (Access Gate) qua HTTP POST để đóng/mở cổng.
  - B5 (Analytics) qua HTTP POST để đồng bộ dữ liệu.

## 9. Hướng dẫn chạy test
Import file `tests/postman_collection.json` vào Postman. Quét qua môi trường `tests/environment_local.json` để giả lập các tín hiệu gửi đến B6.

## 10. Minh chứng demo
Xem thêm hình ảnh hệ thống, kết nối chéo với các nhóm tại thư mục `evidence/` và video tại `evidence/demo_video_link.txt`.
