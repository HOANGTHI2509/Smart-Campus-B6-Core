# Hướng Dẫn Chạy Local (Không dùng Docker)

Trong một số trường hợp test nhanh, bạn có thể chạy ứng dụng trực tiếp bằng Python mà không cần Docker.

### Yêu cầu hệ thống
- Python 3.11 trở lên
- pip (Python package manager)

### Các bước cài đặt và khởi chạy

1. **Clone mã nguồn & vào thư mục dự án:**
   ```bash
   cd B6_Core_Business
   ```

2. **Cài đặt môi trường ảo (Virtual Environment):**
   ```bash
   python -m venv venv
   ```

3. **Kích hoạt môi trường ảo:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Cấu hình môi trường:**
   Tạo file `.env` từ file mẫu:
   ```bash
   cp .env.example .env
   ```
   Sau đó mở file `.env` và điền các thông tin Ngrok/IP LAN của các nhóm B3, B4, B7 và thông tin HiveMQ.

6. **Chạy máy chủ FastAPI:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Kiểm tra hoạt động:**
   - Mở trình duyệt: `http://localhost:8000/dashboard` để xem UI.
   - Kiểm tra Health: `http://localhost:8000/health`
