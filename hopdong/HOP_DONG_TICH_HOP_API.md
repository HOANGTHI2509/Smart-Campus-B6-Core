# 🤝 BIÊN BẢN ĐÀM PHÁN & CHỐT HỢP ĐỒNG API (API CONTRACT AGREEMENT)

**Dự án:** Smart Campus - B6 Core Business
**Người đại diện B6 (Backend Core):** `[Tên của bạn]`
**Các nhóm đối tác cần tích hợp:** 
- Nhóm B3: Hệ thống Cửa kiểm soát (Access Gate / Thẻ từ)
- Nhóm B4: Hệ thống Camera AI (AI Vision / Khuôn mặt)

Tài liệu này là **cam kết kỹ thuật (Contract)** giữa B6 và các nhóm phần cứng/AI. Mọi sự thay đổi về cấu trúc dữ liệu sau khi "chốt sổ" đều phải được thông báo và đồng thuận bằng văn bản.

---

## 🛑 ĐIỀU KHOẢN CHUNG (SLA & BẢO MẬT)
1. **Giao thức:** Tất cả gọi qua giao thức `HTTP/RESTful`, dữ liệu định dạng `application/json`.
2. **Bảo mật (Authentication):** 
   - Nhóm B3 và B4 phải gọi API `/api/v1/access/login` để lấy JWT Token trước khi bắt đầu phiên làm việc.
   - Luôn gắn Token vào Header: `Authorization: Bearer <chuỗi_access_token>`.
3. **Tính toàn vẹn (Idempotency):** Việc B3/B4 bị lỗi mạng và vô tình gửi trùng lặp 1 bản ghi (cùng `student_id`, cùng `timestamp`) sẽ không làm hỏng dữ liệu hệ thống, B6 cam kết sẽ tự động lọc và bỏ qua bản ghi trùng.
4. **Thời gian phản hồi (Latency):** B6 cam kết phản hồi các request quét thẻ trong vòng **< 500ms** để đảm bảo phần cứng (cửa xoay) mở không bị trễ.

---

## 🚪 PHẦN 1: HỢP ĐỒNG VỚI NHÓM B3 (ACCESS GATE / CỔNG QUẸT THẺ)

### API: Xác thực thẻ từ & Ra lệnh mở cửa
- **Endpoint:** `POST /api/v1/access/check`
- **Mô tả:** B3 gửi mã thẻ (UID) khi có người quẹt, B6 sẽ kiểm tra trong CSDL và trả về lệnh có được mở cửa hay không.

**Dữ liệu B3 gửi lên (Request Body):**
```json
{
  "card_uid": "string (bắt buộc, mã thẻ từ lấy từ module RFID)",
  "gate_id": "string (bắt buộc, ID định danh của cái cửa quét)"
}
```

**Dữ liệu B6 trả về (Response 200 OK):**
```json
{
  "status": "success hoặc error",
  "is_granted": true,   // B3 BẮT BUỘC DỰA VÀO TRƯỜNG NÀY (True = MỞ CỬA, False = ĐÓNG CỬA)
  "message": "Xác thực thành công",
  "user_name": "Nguyễn Văn A (Có thể null)" 
}
```

---

## 📷 PHẦN 2: HỢP ĐỒNG VỚI NHÓM B4 (AI VISION / CAMERA NHẬN DIỆN)

### API: Ghi nhận điểm danh bằng Khuôn mặt (Dự kiến)
- **Endpoint:** `POST /api/v1/attendance/face-recognize` 
- **Mô tả:** Camera AI (B4) quét được mặt sinh viên sẽ gửi thẳng mã sinh viên (student_id) về hệ thống Core.

**Dữ liệu B4 gửi lên (Request Body):**
```json
{
  "student_id": "string (bắt buộc)",
  "camera_id": "string (bắt buộc)",
  "confidence_score": 0.95, // (Tùy chọn) Độ chính xác AI nhận diện để B6 làm log
  "timestamp": "2026-06-04T07:00:00Z"
}
```

**Dữ liệu B6 trả về (Response 200 OK):**
```json
{
  "status": "success",
  "message": "Ghi nhận điểm danh/vào cổng thành công"
}
```

---

## ❌ BẢNG MÃ LỖI (ERROR CODES) CHUNG
Các đối tác (B3, B4) bắt buộc phải tự xử lý các mã lỗi HTTP này trên thiết bị màn hình của mình (báo đèn đỏ, kêu tít tít...):

- **`400 Bad Request`**: B3/B4 gửi sai định dạng JSON hoặc thiếu trường bắt buộc.
- **`401 Unauthorized`**: Token bị hết hạn hoặc không truyền Token. *(Cách xử lý: B3/B4 tự động gọi lại hàm Login để lấy Token mới)*.
- **`403 Forbidden`**: Mã thẻ hoặc tài khoản sinh viên đã bị khóa trên hệ thống.
- **`404 Not Found`**: Không tìm thấy mã thẻ/mã sinh viên này trong cơ sở dữ liệu.
- **`500 Internal Server Error`**: Lỗi Server B6 bị sập. *(Cách xử lý: B3/B4 hiển thị lên màn hình "Hệ thống đang bảo trì, vui lòng quay lại sau")*.

---
> **XÁC NHẬN CỦA CÁC BÊN:**
> Chúng tôi đồng ý với cấu trúc Data Contract trên và cam kết không tự ý sửa đổi khi code thật.
> 
> *Ngày chốt Contract: ......./......./2026*
> - **Chữ ký Đại diện B6 (Backend):** .............................
> - **Chữ ký Đại diện B3 (Gate):** .............................
> - **Chữ ký Đại diện B4 (Camera AI):** .............................
