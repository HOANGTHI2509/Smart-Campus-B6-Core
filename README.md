# 🎓 Smart Campus - Phân hệ B6 (Core Business)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

## 📖 Giới thiệu
**Smart Campus (Hệ thống Quản lý Khuôn viên Thông minh)** là một sản phẩm đồ án thực tế của sinh viên **Trường Đại học Đại Nam (DNU)**. 

Dự án này thuộc **Nhóm B6 - Core Business (Xử lý nghiệp vụ trung tâm & Điều phối hệ thống)**, đóng vai trò là "nhạc trưởng" trong toàn bộ kiến trúc Microservices. Phân hệ B6 chịu trách nhiệm tiếp nhận dữ liệu từ các cảm biến IoT và Camera AI, đối chiếu với cơ sở dữ liệu để đưa ra các quyết định kiểm soát tự động và an toàn.

**Tác giả - Nhóm 13 (Lớp CNTT 17-07 - Khoa Công nghệ thông tin):**
- 👨‍💻 **Hoàng Văn Thi** (Trưởng nhóm)
- 👨‍💻 **Đoàn Duy Mạnh**
- 👨‍💻 **Lương Quang Huy**

## 🚀 Tính năng cốt lõi (Features)
- 🗄️ **Quản lý dữ liệu tập trung**: Quản lý thông tin Sinh viên/Giảng viên (Users), Thiết bị IoT (Devices) và Thời khóa biểu (Schedules).
- 🔐 **Kiểm soát ra vào (Access Control)**: Xác thực thẻ từ (RFID/NFC) để cấp quyền truy cập.
- 📡 **Điều phối hệ thống**: Đóng/mở cổng tự động (giao tiếp với phân hệ B3).
- ⚠️ **Hệ thống cảnh báo**: Xử lý và gửi tín hiệu cảnh báo an ninh (giao tiếp với phân hệ B7).
- ⚡ **Hiệu năng cao**: Xử lý API bất đồng bộ với FastAPI giúp đáp ứng độ trễ cực thấp cho các thiết bị IoT.

## 🏗️ Kiến trúc (Architecture)
Phân hệ B6 hoạt động dựa trên kiến trúc Microservices và giao tiếp qua các chuẩn API/Protocol:
- **Nhận tín hiệu**: Từ Camera AI (B2) và Cảm biến môi trường (B1).
- **Truy vấn Database**: Kiểm tra quyền hạn và thời khóa biểu của User qua MySQL.
- **Ra quyết định**: 
  - Gửi lệnh MỞ/ĐÓNG cổng cho Access Gate (B3).
  - Gửi Notification cảnh báo nếu phát hiện xâm nhập trái phép (B7).

## 🛠️ Hướng dẫn Cài đặt & Chạy dự án (Getting Started)

### Yêu cầu môi trường (Prerequisites)
- **Python 3.10+**
- **Docker & Docker Compose**

### Các bước chạy
1. **Clone repository về máy local:**
   ```bash
   git clone https://github.com/HOANGTHI2509/Smart-Campus-B6-Core.git
   cd Smart-Campus-B6-Core
   ```

2. **Khởi động Database MySQL bằng Docker:**
   ```bash
   docker-compose up -d
   ```

3. **Cài đặt các thư viện (nếu dùng môi trường ảo):**
   ```bash
   pip install -r requirements.txt
   ```

4. **Khởi động Server FastAPI:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## 📚 Tài liệu API (API Documentation)
Sau khi server chạy thành công, bạn có thể truy cập hệ thống tài liệu API tự động (Swagger UI) tại:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

## 🎓 Bản quyền & Ghi chú (License & Acknowledgements)
- 🎉 Xin gửi lời cảm ơn chân thành tới các **Giảng viên hướng dẫn** và **Trường Đại học Đại Nam (DNU)** đã hỗ trợ và tạo điều kiện tốt nhất để nhóm hoàn thành đồ án này.
- Mã nguồn được phát triển nhằm mục đích học tập và nghiên cứu trong khuôn khổ môn học của Khoa Công nghệ thông tin - DNU.
