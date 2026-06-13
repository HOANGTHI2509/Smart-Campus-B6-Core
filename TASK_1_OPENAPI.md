# 📋 TÀI LIỆU GIAO VIỆC - THÀNH VIÊN 1 (TRƯỞNG NHÓM)

**Người phụ trách:** Thi
**Vai trò:** System Architect & Core Logic Developer (Đồ án hoàn chỉnh)

## 🎯 MỤC TIÊU CÔNG VIỆC
Chịu trách nhiệm thiết kế kiến trúc Database cốt lõi, viết logic thuật toán cấp phép ra/vào và tích hợp giao tiếp trực tiếp với phân hệ B3 (Access Gate) và B7 (Notification). Đồng thời quản lý code và review tiến độ toàn đội.

## 📝 DANH SÁCH TASK CHI TIẾT

### 1. Thiết kế & Khởi tạo Database (Database Architecture)
- [x] Rà soát file OpenAPI đảm bảo tuân thủ chuẩn OpenAPI 3.1. (Đã hoàn thành ở Lab trước)
- [x] Thiết kế ERD (Sơ đồ thực thể) cho MySQL: Bảng `Users`, `Roles`, `Schedules`, `Devices`, `AccessLogs`.
- [x] Viết file migration để tạo database tự động.

### 2. Xây dựng thuật toán Cấp phép ra/vào (Linh hồn của hệ thống)
- [x] Viết Service kiểm tra tính hợp lệ: Nhận ID nhân sự/sinh viên ➔ Đối chiếu `Schedules` ➔ Đối chiếu thẻ có bị khóa không.
- [x] Xử lý logic luồng ngoại lệ (đi trễ, quyền đặc biệt của giảng viên/admin).

### 3. Tích hợp Outbound API (Gọi sang B3 và B7)
- [ ] Viết module HTTP Client gửi lệnh `POST` gọi API của B3 ra lệnh mở cổng khi hợp lệ.
- [ ] Viết module gọi API của B7 để gửi tín hiệu cảnh báo khi phát hiện đột nhập.

### 4. Triển khai & Quản lý dự án
- [ ] Cấu hình server/VPS để deploy dự án lên môi trường live cho các nhóm khác gọi vào.
- [ ] Duyệt Pull Request của Mạnh và Huy trên Git.
- [ ] Merge code nhánh `dev` sang `main`, chốt bản Release.

