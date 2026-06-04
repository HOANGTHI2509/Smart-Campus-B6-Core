# 📋 TÀI LIỆU GIAO VIỆC - THÀNH VIÊN 2 (POSTMAN & MOCK SERVER)

**Người phụ trách:** Mạnh
**Vai trò:** Postman Testing Lead (Lab 04)


## 🎯 MỤC TIÊU CÔNG VIỆC (DÀNH CHO LAB 04)
Xây dựng bộ test hoàn chỉnh trên Postman dựa theo OpenAPI, cấu hình môi trường test và duy trì Mock Server để 2 nhóm đối tác (B3, B4) gọi test.

## 📝 DANH SÁCH TASK CHI TIẾT

### 1. Xây dựng Postman Collection
- [ ] Import file OpenAPI vào Postman để tạo Collection gốc.
- [ ] Cấu hình Postman Environments (`local`, `mock`) để loại bỏ hoàn toàn các giá trị hardcode trong URL.
- [ ] Bổ sung các test script (chạy bằng Javascript trong tab Tests của Postman) để verify HTTP Status và JSON schema.

### 2. Cấu hình Mock Server cho B3 & B4
- [ ] Thiết lập Mock Server trên Postman để trả về mock data dựa trên các ví dụ (examples) đã định nghĩa.
- [ ] Chia sẻ link Mock Server cho nhóm B3 và B4 để họ test chéo trước khi Backend thật hoàn thiện.
- [ ] Xử lý các lỗi 404 (Not Found) nếu Mock Server mapping không đúng đường dẫn.

### 3. Viết kịch bản Test chi tiết
- [ ] **Functional Test:** Kiểm tra luồng chạy đúng (Happy path).
- [ ] **Negative Test:** Bắn dữ liệu sai (Thiếu field, sai UUID) xem API có báo lỗi chuẩn không.
- [ ] **Auth Test:** Kiểm tra các API yêu cầu Token có chặn truy cập trái phép không.

