# 📋 TÀI LIỆU GIAO VIỆC - THÀNH VIÊN 3

**Người phụ trách:** Huy
**Vai trò:** Integration, Security & DevOps (Đồ án hoàn chỉnh)

## 🎯 MỤC TIÊU CÔNG VIỆC
Chịu trách nhiệm viết các API hứng dữ liệu từ bên ngoài (B1, B4), thiết lập cơ chế bảo mật (JWT) cho hệ thống và đóng gói toàn bộ ứng dụng bằng Docker để chạy CI/CD.

## 📝 DANH SÁCH TASK CHI TIẾT

### 1. Xây dựng API Webhook hứng dữ liệu (Inbound API)
- [ ] Viết API hứng dữ liệu thẻ từ/RFID từ phân hệ B1 (IoT Ingestion).
- [ ] Viết API hứng kết quả nhận diện khuôn mặt (JSON chứa list `user_id`) từ phân hệ B4 (AI Vision).
- [ ] Truyền dữ liệu nhận được vào hàm xử lý thuật toán cốt lõi do Trưởng nhóm (Thi) viết.

### 2. Bảo mật API (Security & Authentication)
- [ ] Cài đặt hệ thống bảo mật bằng JWT Token cho các API nội bộ và API public.
- [ ] Mã hóa mật khẩu người dùng trong Database (sử dụng bcrypt hoặc tương đương).

### 3. Triển khai & CI/CD (DevOps)
- [ ] Viết `Dockerfile` và `docker-compose.yml` đóng gói ứng dụng (FastAPI + MySQL).
- [ ] Viết script `.github/workflows` tự động test và deploy.
