# Kịch Bản Kiểm Thử Chức Năng (Functional Test Cases)
**Phân hệ:** Core Business (B6) tích hợp Access Gate (B3) & AI Vision (B4)

---

## 🟢 Test Case 1: Quẹt thẻ hợp lệ, khuôn mặt người thật và khớp > 90% (Happy Path)
- **Input:** 
  - `cardId`: "RFID-2026-001" (Đang kích hoạt, đủ tiền/quyền).
  - `imageRef`: Ảnh khuôn mặt chính diện rõ nét.
- **Action:** 
  - B3 gọi `POST /access/check` gửi kèm `Idempotency-Key`.
  - B6 gọi `POST /vision/face-match` sang B4.
- **Expected Business Result:** 
  - B4 phản hồi `confidence: 0.95`, `status: success`, `isLive: true`.
  - B6 ghi log thành công và ra lệnh mở cổng.
- **Pass/Fail Rule:** 
  - **PASS:** Hệ thống B6 trả về `HTTP 200`, `decision: ALLOW`. Tiền/quyền chỉ trừ đúng 1 lượt. Log hiển thị sinh viên đã vào.
  - **FAIL:** Trả về mã lỗi, hoặc cổng không nhận được lệnh ALLOW, hoặc delay quá 1.5 giây.

---

## 🔴 Test Case 2: Phát hiện gian lận hình ảnh (Spoofing / Liveness Detection)
- **Input:** 
  - `cardId`: "RFID-2026-002" (Hợp lệ).
  - `imageRef`: Ảnh giơ điện thoại chứa ảnh mặt hoặc đeo mặt nạ giấy.
- **Action:** 
  - B3 gọi `POST /access/check`.
  - B6 gọi sang B4 phân tích ảnh.
- **Expected Business Result:** 
  - B4 phân tích và trả về `isLive: false` (Phát hiện gian lận).
  - B6 từ chối mở cổng, đồng thời bắn event `core.alert.created` sang hệ thống Notification (B7) để báo bảo vệ.
- **Pass/Fail Rule:** 
  - **PASS:** Hệ thống trả về `HTTP 200` với `decision: DENY`, `reasonCode: SPOOFING_DETECTED`. Cổng B3 không mở.
  - **FAIL:** Hệ thống trả về `ALLOW` do bị đánh lừa bởi `faceMatched: true` mà bỏ qua cờ `isLive`.

---

## 🟡 Test Case 3: Xử lý quẹt thẻ rác/spam liên tục (Idempotency)
- **Input:** 
  - 3 request giống y hệt nhau chứa cùng `cardId: RFID-2026-003` và cùng một `Idempotency-Key`.
- **Action:** 
  - B3 bắn đồng thời (concurrent) 3 request `POST /access/check` vào B6 trong vòng 0.5 giây.
- **Expected Business Result:** 
  - B6 nhận request đầu tiên, đưa vào xử lý và gài khóa (Lock) trên Redis.
  - 2 request sau đến bị chặn lại do trùng Key.
- **Pass/Fail Rule:** 
  - **PASS:** Hệ thống trả về 1 lần xử lý thành công, 2 lần sau trả về `HTTP 409 Conflict` (hoặc trả lại data cũ). Tài khoản sinh viên không bị trừ lặp 3 lần. Log chỉ ghi nhận 1 lượt truy cập.
  - **FAIL:** Hệ thống sập, hoặc thẻ bị trừ tiền/ghi nhận 3 lượt qua cổng cùng 1 giây.

---

## 🟠 Test Case 4: Ảnh mờ, người thật nhưng không nhận diện được (Low Confidence)
- **Input:** 
  - `cardId`: "RFID-2026-004" (Hợp lệ).
  - `imageRef`: Bức ảnh chụp buổi tối, thiếu sáng, bị nhòe.
- **Action:** 
  - B6 gọi B4. B4 trả về `status: low_confidence` và `faceMatched: false`.
- **Expected Business Result:** 
  - Do thẻ hợp lệ và đây là khuôn mặt thật (không bị spoofing), Core Business ưu tiên **MỞ CỔNG** để chống ách tắc giờ cao điểm.
  - Tuy nhiên, hệ thống đánh dấu "Cần kiểm toán bằng tay" (Manual Audit Required) vào log.
- **Pass/Fail Rule:** 
  - **PASS:** Trả về `decision: ALLOW`. Log của B6 lưu trường `auditRequired: true`.
  - **FAIL:** Hệ thống báo lỗi HTTP 500, đơ server do không biết xử lý trạng thái mờ, hoặc văng lỗi `HTTP 422`.

---

## 🟣 Test Case 5: Cổng mở nhưng sinh viên "quay xe" (Physical Timeout)
- **Input:** 
  - Trạng thái trước: Cổng vừa nhận lệnh `ALLOW` và mở ra.
- **Action:** 
  - Sinh viên đổi ý đi lùi lại.
  - Sau 5 giây, cảm biến hồng ngoại tại Gate (B3) không bị cắt ngang, cổng đóng lại.
  - B3 bắn event `POST /events` với `status: ACCESS_CANCELLED`.
- **Expected Business Result:** 
  - B6 nhận sự kiện và thực hiện **Rollback** (Hoàn trả tiền hoặc xóa bỏ log "Đã vào trường").
- **Pass/Fail Rule:** 
  - **PASS:** Trạng thái sinh viên được hoàn lại thành "Đang ở ngoài trường". Truy vấn lại `GET /access/logs` trạng thái cập nhật đúng thành `CANCELLED`.
  - **FAIL:** B6 không có cơ chế rollback, đinh ninh sinh viên đã vào trường dẫn đến sai lệch sổ sách kiểm toán cuối ngày.
