# 🎓 Smart Campus - Phân hệ B6 (Core Business)

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</div>

<br>

## 📖 Giới thiệu chung
**Smart Campus (Hệ thống Quản lý Khuôn viên Thông minh)** là đồ án thực tế của sinh viên **Trường Đại học Đại Nam (DNU)**. 

Thuộc **Nhóm B6 - Core Business**, phân hệ này đóng vai trò là "Nhạc trưởng" (Trái tim của hệ thống). B6 chịu trách nhiệm tiếp nhận dữ liệu từ các cảm biến IoT (B1) và Camera AI (B4), đối chiếu với Cơ sở dữ liệu để đưa ra các quyết định kiểm soát tự động mở/đóng cổng (B3) và phát tín hiệu an ninh (B7).

---

## 👥 Đội ngũ phát triển (Nhóm 13 - Lớp CNTT 17-07)

*Lưu ý: Theo hướng dẫn của môn học, nhóm 3 thành viên đã phân chia và bao quát đầy đủ 4 vai trò bắt buộc (Team Lead kiêm 2 vai).*

| Thành viên | Vai trò chuẩn | Nhiệm vụ chi tiết (Làm minh chứng đánh giá) |
| :--- | :--- | :--- |
| 👑 **Hoàng Văn Thi** | **Service Lead** & **Backend Developer** | - **(Service Lead):** Nắm vững yêu cầu hệ thống, phân công task. Đại diện nhóm đàm phán hợp đồng API với các nhóm B3, B4, B7.<br>- **(Backend Dev):** Trực tiếp code logic nghiệp vụ trung tâm (`app/main.py`), xây dựng Rule Engine (Xử lý chống Spam, cấm quẹt đêm, gọi webhook). |
| 👨‍💻 **Đoàn Duy Mạnh** | **API/Contract Owner** | - Chịu trách nhiệm thiết kế toàn bộ hợp đồng giao tiếp.<br>- Trực tiếp viết file `openapi.yaml` chuẩn OpenAPI 3.1.0 (Có schema, example, error model).<br>- Cập nhật và quản lý tài liệu `endpoint_catalog.md` để cung cấp cho nhóm khác. |
| 👨‍💻 **Lương Quang Huy** | **Test & DevOps Owner** | - **(DevOps):** Viết `Dockerfile`, thiết lập `docker-compose.yml`, cấu hình file `.env` và `healthcheck` chạy repo sạch.<br>- **(Test):** Tạo bộ Collection trên Postman phủ các case (Happy, Negative, Boundary). Quay video minh chứng End-to-End và xuất Report kiểm thử. |

---

## 🚀 Tính năng cốt lõi (Core Features)
- 🗄️ **Quản lý CSDL Tập trung**: Quản lý thông tin Người dùng, Thiết bị, và Thời khóa biểu.
- 🔐 **Kiểm soát ra vào thông minh**: Xử lý logic cấp phép dựa trên thời khóa biểu và quyền hạn (Admin/Giảng viên/Sinh viên).
- 📡 **Tích hợp hệ sinh thái Microservices**: Giao tiếp mượt mà với Access Gate (B3), Notification (B7), AI Vision (B4).
- 🛡️ **Bảo mật**: Xác thực bằng JWT Token, mã hóa thông tin nhạy cảm.
- ⚡ **Hiệu năng cao**: Xử lý API bất đồng bộ với FastAPI giúp đáp ứng hàng ngàn thiết bị kết nối cùng lúc.

---

## 🛠️ Quy định làm việc & Git Workflow (QUAN TRỌNG)

Để tránh **xung đột code (conflict)** và làm hỏng dự án, toàn đội **BẮT BUỘC** phải tuân thủ quy trình Git sau:

### 1. Phân chia Nhánh (Branching Strategy)
- 🔴 **Nhánh `main`:** Nhánh CHỐT CODE. Chứa phiên bản Release an toàn, ổn định 100%. **Tuyệt đối không push thẳng code lên nhánh này**.
- 🟡 **Nhánh `dev`:** Nhánh TÍCH HỢP. Đây là nơi code của 3 thành viên gộp chung lại với nhau để chạy thử và kiểm tra sự tương thích.
- 🟢 **Nhánh cá nhân (Feature Branch):** Mỗi thành viên khi làm một chức năng mới bắt buộc phải rẽ nhánh từ `dev`.
  - Cú pháp: `<tên>-feature-<chức-năng>` 
  - VD: `thi-feature-core-logic`, `manh-feature-crud-api`

### 2. Quy trình Code & Đẩy Code an toàn
1. **Pull Code mới nhất:** Trước khi làm việc, phải đảm bảo nhánh `dev` ở máy mình là mới nhất: `git checkout dev` ➔ `git pull origin dev`.
2. **Code trên nhánh riêng:** `git checkout -b <nhánh-cá-nhân>` và bắt đầu code.
3. **Lưu & Đẩy code:** `git add .` ➔ `git commit -m "mô tả rõ ràng"` ➔ `git push origin <nhánh-cá-nhân>`.
4. **Pull Request (Yêu cầu gộp code):** Truy cập GitHub, tạo PR ghép nhánh cá nhân vào `dev`.
5. **Code Review:** Chờ **Leader (Thi)** kiểm tra code. Nếu code chuẩn, không lỗi, Leader sẽ duyệt Merge vào `dev`.
6. **Release:** Khi mọi chức năng trên `dev` đã hoạt động trơn tru, Leader sẽ merge `dev` vào `main` để chốt phiên bản báo cáo với Giảng viên.

---

## 💻 Hướng dẫn Cài đặt & Chạy dự án (Bằng Docker)

Đây là cách khởi chạy chuẩn nhất để đảm bảo service hoạt động ổn định và có sẵn cấu hình mạng nội bộ.

**1. Clone dự án và thiết lập môi trường:**
```bash
git clone https://github.com/HOANGTHI2509/Smart-Campus-B6-Core.git
cd Smart-Campus-B6-Core
# Tạo file .env từ file mẫu
cp .env.example .env
```
*(Lưu ý: Mở file `.env` lên để kiểm tra/sửa lại chuỗi kết nối **PostgreSQL** và IP của các nhóm khác).*

**2. Khởi chạy toàn bộ hệ thống bằng Docker:**
Chỉ cần chạy 1 lệnh duy nhất, Docker sẽ tự động build image và khởi động B6 API Gateway:
```bash
docker-compose up --build -d
```

**3. Kiểm tra trạng thái:**
```bash
# Xem log để đảm bảo hệ thống kết nối thành công với MQTT và không có lỗi
docker-compose logs -f
```

📚 Hệ thống tài liệu API tự động (Swagger UI) sẽ mở tại: 👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**
*(Để chạy bằng Python thuần mà không qua Docker, vui lòng đọc chi tiết hướng dẫn tại file `RUN_LOCAL.md`)*
