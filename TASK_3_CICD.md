# 📋 TÀI LIỆU GIAO VIỆC - THÀNH VIÊN 3 (CI/CD, NEWMAN & REPORTING)

**Người phụ trách:** Huy
**Vai trò:** Automation & Reporting Lead (Lab 04)

> ⚠️ **LƯU Ý QUAN TRỌNG:** Trước khi thực hiện bất kỳ task nào và sử dụng AI (như Antigravity/Gemini), bạn **BẮT BUỘC** phải đọc và tuân thủ file `AI_PROMPT_CONTRACT.md`.

## 🎯 MỤC TIÊU CÔNG VIỆC (DÀNH CHO LAB 04)
Tự động hóa việc chạy test bằng Newman, tích hợp vào CI/CD (GitHub Actions) và chuẩn bị toàn bộ minh chứng (Evidence) để nghiệm thu Lab 04 với Giảng viên.

## 📝 DANH SÁCH TASK CHI TIẾT

### 1. Automation Testing với Newman
- [ ] Cài đặt và cấu hình Newman (Postman CLI) để chạy test tự động ở local.
- [ ] Xuất Postman Collection và Environment ra file JSON lưu vào thư mục `postman/`.
- [ ] Viết lệnh chạy Newman kèm theo htmlextra reporter để sinh ra báo cáo HTML/XML đẹp mắt.

### 2. Tích hợp CI/CD
- [ ] Đẩy (Push) toàn bộ thư mục `postman/` (gồm collection, environment data) lên Git.
- [ ] Viết script `.github/workflows/test.yml` để mỗi khi có người push code hoặc cập nhật API Contract, CI sẽ tự động chạy Newman test.

### 3. Thu thập Evidence & Điền Checklist
- [ ] Chạy toàn bộ test suites, đảm bảo pass 100% các tiêu chí Reliability và Functional.
- [ ] Lấy các báo cáo HTML xuất ra, lưu vào thư mục `reports/`.
- [ ] Điền các form "Contract Testing Matrix" và "Checklist Lab 04" theo form mẫu của môn học để nộp báo cáo cuối cùng.

---

## 🤖 HƯỚNG DẪN PROMPT AI DÀNH RIÊNG CHO ROLE NÀY
Khi nhờ AI viết script tự động, hãy dán câu này lên đầu:
> *"Tôi là thành viên của dự án. Hãy đọc kỹ và tuân thủ tuyệt đối các quy tắc trong file `AI_PROMPT_CONTRACT.md`. Đóng vai trò là DevOps/Automation QA, hãy giúp tôi viết GitHub Actions workflow để chạy Newman test tự động với file Collection và Environment tôi cung cấp, sau đó xuất report HTML."*
