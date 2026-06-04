# 📋 TÀI LIỆU GIAO VIỆC - THÀNH VIÊN 1 (OPENAPI & CONTRACT DESIGN)

**Người phụ trách:** Thi
**Vai trò:** OpenAPI & Contract Lead (Lab 04)

> ⚠️ **LƯU Ý QUAN TRỌNG:** Trước khi thực hiện bất kỳ task nào và sử dụng AI (như Antigravity/Gemini), bạn **BẮT BUỘC** phải đọc và tuân thủ file `AI_PROMPT_CONTRACT.md`.

## 🎯 MỤC TIÊU CÔNG VIỆC (DÀNH CHO LAB 04)
Đảm bảo bản hợp đồng API (OpenAPI 3.1) của hệ thống B6 (Core Business) hoàn hảo, không có lỗi linting và được thống nhất chặt chẽ với 2 nhóm đối tác (B3 - Access Gate và B4 - AI Vision).

## 📝 DANH SÁCH TASK CHI TIẾT

### 1. Chuẩn hóa OpenAPI Specification
- [ ] Rà soát file `openapi.yaml` / `openapi.json` đảm bảo tuân thủ chuẩn OpenAPI 3.1.
- [ ] Chạy công cụ linting (Spectral) để phát hiện và sửa các lỗi về cấu trúc, naming convention.
- [ ] Đảm bảo các kiểu dữ liệu (UUID, URI, Data format) được định nghĩa chặt chẽ để vượt qua tool check.

### 2. Giao tiếp & Chốt Contract với Đối tác (B3 & B4)
- [ ] Cung cấp API Contract cho nhóm B3 (Thiết bị cổng kiểm soát) để họ tích hợp tính năng check-in.
- [ ] Cung cấp API Contract cho nhóm B4 (AI Camera) để họ gửi dữ liệu nhận diện khuôn mặt về.
- [ ] Ký biên bản chốt các trường dữ liệu (Request/Response) với 2 nhóm này để tránh đổi logic phút chót.

---

## 🤖 HƯỚNG DẪN PROMPT AI DÀNH RIÊNG CHO ROLE NÀY
Mỗi khi cần AI hỗ trợ sửa lỗi file spec, hãy dán câu này lên đầu:
> *"Tôi là thành viên của dự án. Hãy đọc kỹ và tuân thủ tuyệt đối các quy tắc trong file `AI_PROMPT_CONTRACT.md`. Đóng vai trò là OpenAPI Expert, hãy giúp tôi fix các lỗi Spectral linting trong file OpenAPI của tôi. Tuyệt đối không thay đổi business logic, chỉ sửa syntax cho chuẩn OpenAPI 3.1."*
