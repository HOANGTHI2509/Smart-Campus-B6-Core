# 📑 TÀI LIỆU QUẢN LÝ VÀ PHÂN CÔNG DỰ ÁN (LAB 04)

**Dự án:** Smart Campus - B6 Core Business  
**Giai đoạn:** Lab 04 (API Contract Testing & Integration)  
**Mục tiêu cốt lõi:** Hoàn thiện API Contract (OpenAPI 3.1), triển khai Postman Mock Server, tự động hóa kiểm thử bằng Newman, và chốt giao thức kết nối với 2 nhóm đối tác (B3 - Access Gate, B4 - AI Vision).

---

## 1. QUY ĐỊNH LÀM VIỆC CHUNG
Để đảm bảo tính chuyên nghiệp và toàn vẹn của dự án, toàn bộ thành viên **BẮT BUỘC** tuân thủ nguyên tắc sau:
1. **Sử dụng AI có kiểm soát:** Đọc và tuân thủ chặt chẽ Hợp đồng AI tại file `AI_PROMPT_CONTRACT.md`. Mọi câu lệnh nhờ AI hỗ trợ đều phải có ngữ cảnh rõ ràng và không được phá vỡ kiến trúc chung.
2. **Quy trình Review:** Mọi thay đổi về kiến trúc hệ thống, cấu trúc Database, hay logic API cốt lõi đều phải được thông qua nhóm trước khi Merge vào nhánh chính.
3. **Giữ gìn Codebase:** Không tự ý xóa, sửa comment, docstring hay code của người khác nếu không thuộc scope công việc của mình.

---

## 2. CHI TIẾT PHÂN CÔNG THEO VAI TRÒ

### 👤 VAI TRÒ 1: OPENAPI & CONTRACT LEAD
**Nhân sự phụ trách:** `[Điền tên thành viên 1]`
**Mô tả công việc:** Quản trị đặc tả kỹ thuật API, định hình cấu trúc dữ liệu và đàm phán hợp đồng với các hệ thống bên ngoài.

**Nhiệm vụ cụ thể:**
- **Chuẩn hóa OpenAPI:** Rà soát và cập nhật file `openapi.yaml` (hoặc `.json`) đảm bảo tuân thủ chuẩn OpenAPI 3.1. Các kiểu dữ liệu (UUID, URI) phải được định nghĩa chặt chẽ.
- **Xử lý Linting:** Cấu hình và sử dụng công cụ Spectral để rà soát, phát hiện và khắc phục toàn bộ các lỗi về cấu trúc, naming convention trong file đặc tả.
- **Chốt Hợp đồng với Đối tác:** Trực tiếp làm việc với nhóm B3 và B4. Cung cấp API Contract, thống nhất các trường Request/Response. Đảm bảo cam kết về tính Consistency và Idempotency (gọi nhiều lần không thay đổi kết quả ngoài ý muốn).

---

### 👤 VAI TRÒ 2: POSTMAN TESTING & MOCK SERVER LEAD
**Nhân sự phụ trách:** `[Điền tên thành viên 2]`
**Mô tả công việc:** Chịu trách nhiệm xây dựng hệ thống kiểm thử thủ công trên Postman và vận hành môi trường giả lập (Mock Server).

**Nhiệm vụ cụ thể:**
- **Quản trị Postman Workspace:** Import file OpenAPI vào Postman để khởi tạo Collection. Thiết lập môi trường biến (Environments: Local, Mock) để loại bỏ việc hardcode các URL/Tham số.
- **Xây dựng Mock Server:** Triển khai Mock Server trên Postman dựa trên các Data Examples định nghĩa sẵn. Chia sẻ endpoint giả lập này cho nhóm B3, B4 để họ test chéo trước khi Backend thực tế hoàn thiện. Xử lý triệt để các lỗi 404 do mapping sai route.
- **Thiết kế Test Scripts:** Viết các script Javascript (trong thẻ Tests của Postman) để kiểm thử chức năng (Functional), kiểm thử luồng lỗi (Negative), và kiểm thử xác thực (Auth).

---

### 👤 VAI TRÒ 3: AUTOMATION, CI/CD & REPORTING LEAD
**Nhân sự phụ trách:** `[Điền tên thành viên 3]`
**Mô tả công việc:** Tự động hóa toàn bộ quá trình kiểm thử, vận hành CI/CD pipeline và chuẩn bị hồ sơ minh chứng nghiệm thu.

**Nhiệm vụ cụ thể:**
- **Cấu hình Newman Automation:** Tích hợp công cụ Newman (Postman CLI). Trích xuất file Postman Collection và Environment JSON lưu trữ quản lý tại thư mục `postman/`.
- **Thiết lập CI/CD (GitHub Actions):** Viết script workflow (`.github/workflows/test.yml`) để tự động kích hoạt luồng chạy Newman Test mỗi khi có thành viên Push/Pull Request code mới.
- **Nghiệm thu & Báo cáo:** Cấu hình thư viện `htmlextra` để sinh báo cáo kiểm thử định dạng HTML/XML (lưu tại `reports/`). Tổng hợp kết quả, điền form "Contract Testing Matrix" và các Check-list đánh giá bắt buộc của Lab 04.

---

## 3. QUY TRÌNH PHỐI HỢP & TÍCH HỢP (WORKFLOW)
Để công việc diễn ra trơn tru, nhóm áp dụng luồng làm việc nối tiếp như sau:

1. **Bước 1 (Thành viên 1):** Rà soát và fix xong file OpenAPI ➔ *Thông báo hoàn tất & Push code*.
2. **Bước 2 (Thành viên 2):** Lấy file OpenAPI chuẩn từ TV1 ➔ Tạo Postman Collection ➔ Deploy Mock Server ➔ Chia sẻ URL cho đối tác B3, B4 ➔ Bổ sung Test Scripts.
3. **Bước 3 (Thành viên 3):** Export Collection & Env từ TV2 ➔ Viết lệnh chạy Newman ➔ Tích hợp GitHub Actions ➔ Lấy Report ➔ Khớp vào Checklist nghiệm thu.

> 📌 *Tài liệu này là cơ sở để minh bạch công việc và đánh giá chéo giữa các thành viên. Yêu cầu mọi người nghiêm túc tuân thủ.*
