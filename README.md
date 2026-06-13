# 🎓 Smart Campus - Phân hệ B6 (Core Business)

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL">
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</div>

<br>

## 📖 Giới thiệu chung
**Smart Campus (Hệ thống Quản lý Khuôn viên Thông minh)** là đồ án thực tế của sinh viên **Trường Đại học Đại Nam (DNU)**. 

Thuộc **Nhóm B6 - Core Business**, phân hệ này đóng vai trò là "Nhạc trưởng" (Trái tim của hệ thống). B6 chịu trách nhiệm tiếp nhận dữ liệu từ các cảm biến IoT (B1) và Camera AI (B4), đối chiếu với Cơ sở dữ liệu để đưa ra các quyết định kiểm soát tự động mở/đóng cổng (B3) và phát tín hiệu an ninh (B7).

---

## 👥 Đội ngũ phát triển (Nhóm 13 - Lớp CNTT 17-07)

| Thành viên | Vai trò | Nhiệm vụ chính |
| :--- | :--- | :--- |
| 👑 **Hoàng Văn Thi** | **System Architect & Team Lead** | Thiết kế Database (ERD), viết logic Thuật toán cấp phép ra/vào cốt lõi, tích hợp API ngoại vi (B3, B7). Review code và merge nhánh `dev` sang `main`. |
| 👨‍💻 **Đoàn Duy Mạnh** | **API Developer & QA/Tester** | Xây dựng CRUD API, cung cấp Data API cho B5 (Analytics), xây dựng kịch bản kiểm thử Postman. |
| 👨‍💻 **Lương Quang Huy** | **Integration, Security & DevOps** | Viết Inbound Webhooks (hứng data từ B1, B4), mã hóa bảo mật JWT, cấu hình Docker và CI/CD Pipelines. |

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

## 💻 Hướng dẫn Cài đặt & Chạy dự án (Local)

**1. Clone dự án và tạo môi trường:**
```bash
git clone https://github.com/HOANGTHI2509/Smart-Campus-B6-Core.git
cd Smart-Campus-B6-Core
python -m venv .venv
source .venv/Scripts/activate  # (Với Windows: .venv\Scripts\activate)
```

**2. Cài đặt thư viện:**
```bash
pip install -r requirements.txt
```

**3. Khởi tạo Database & Chạy server:**
- Cấu hình file `.env` chứa chuỗi kết nối MySQL (`DATABASE_URL`).
- Chạy tự động tạo bảng trong CSDL:
```bash
python app/core/database.py
```
- Khởi chạy ứng dụng FastAPI:
```bash
python -m uvicorn app.main:app --reload
```

📚 Hệ thống tài liệu API tự động (Swagger UI) sẽ mở tại: 👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**
