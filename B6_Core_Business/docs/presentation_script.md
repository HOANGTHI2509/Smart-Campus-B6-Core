# Kịch bản Thuyết trình Bảo vệ Đồ án - Nhóm 13 (Phân hệ B6)

Kịch bản này được thiết kế chuẩn xác theo **Sơ đồ 6 bước** của tiêu chí chấm điểm, chia đều cho 3 thành viên dựa trên vai trò thực tế để chứng minh sự đóng góp đồng đều.

---

## 🎤 PHẦN 1: TỔNG QUAN & XỬ LÝ LÕI (Do Hoàng Văn Thi - Leader trình bày)

**1. Vai trò của nhóm (Bước 1)**
> *"Dạ em chào Thầy/Cô, em là Thi, đại diện nhóm 13 xin trình bày về phân hệ **B6 - Core Business**. 
> Trong hệ thống Smart Campus, B6 đóng vai trò là "Bộ não trung tâm" (Policy Engine). Nhóm em hoạt động với cả 2 vai trò: Là **Consumer** (nhận dữ liệu từ cổng và cảm biến) và là **Provider** (đưa ra quyết định và gửi lệnh đi các nơi khác)."*

**2. Input (Bước 2)**
> *"Đầu vào của B6 là các sự kiện thô đến từ 3 nhóm:
> - **Nhận từ nhóm B1 (IoT):** Nhận bản tin cảnh báo nhiệt độ cao qua giao thức MQTT.
> - **Nhận từ nhóm B4 (AI Vision):** Nhận ảnh nhận diện khuôn mặt hoặc tín hiệu báo cháy qua Webhook (REST API).
> - **Nhận từ nhóm B3 (Access Gate):** Nhận thông tin thẻ RFID vừa quẹt qua phương thức HTTP POST."*

**3. Xử lý nghiệp vụ (Bước 3)**
> *"Khi nhận Input, B6 không đẩy đi ngay mà đưa qua Rule Engine để tính toán:
> - **Luồng xử lý B1/B4 (Báo cháy):** Đánh giá mức độ rủi ro (risk_level). Nếu là CRITICAL, kích hoạt ngay lệnh khẩn cấp.
> - **Luồng xử lý B3 (Quẹt thẻ):** Áp dụng thuật toán Anti-passback (cấm 1 thẻ quẹt 2 lần trong 5 giây) và luật cấm quẹt thẻ ngoài giờ hành chính (22h đêm - 6h sáng). Mọi vi phạm đều bị chặn đứng!"*
> *(Bấm slide chuyển sang cho Mạnh)*

---

## 🎤 PHẦN 2: HỢP ĐỒNG API & LUỒNG ĐẦU RA (Do Đoàn Duy Mạnh - API Owner trình bày)

**4 & 5. Output và Gửi cho ai? (Bước 4 & Bước 5)**
> *"Chào Thầy/Cô, em là Mạnh. Dựa vào kết quả xử lý của bạn Thi, service B6 sẽ đóng gói Output chuẩn JSON và gọi API điều phối đến đúng các nhóm đích như sau:
> 
> - **Luồng 1 (Từ B3 gửi lại B3):** Khi B3 gửi UID, nếu thẻ hợp lệ, B6 trả về ngay HTTP 200 `{"allowed": true}` để **nhóm B3** mở cổng.
> - **Luồng 2 (Từ B3 gửi sang B7):** Nếu B3 gửi thẻ lạ hoặc cố tình spam thẻ, B6 sẽ từ chối mở cổng, ĐỒNG THỜI tự động gọi API `POST /notify/send` sang **nhóm B7 (Notification)** kèm mã lỗi để kích hoạt còi báo động tại chỗ.
> - **Luồng 3 (Từ B1/B4 gửi sang B7 & B3):** Khi nhận tín hiệu cháy nổ từ B1 hoặc B4, B6 sẽ lập tức gửi lệnh hú còi sang **B7**, đồng thời gọi lệnh khẩn cấp sang **B3** yêu cầu mở bung tất cả các cổng để thoát hiểm.
> - **Luồng 4 (Đồng bộ B5):** Bất kể sự kiện nào diễn ra, B6 đều đóng gói gửi một bản copy Log sang **nhóm B5 (Analytics)** để họ lưu trữ và vẽ biểu đồ."*
> *(Nhường chuột/mic cho Huy)*

---

## 🎤 PHẦN 3: MINH CHỨNG VẬN HÀNH THỰC TẾ (Do Lương Quang Huy - Test & DevOps trình bày)

**6. Minh chứng Demo (Bước 6)**
> *"Em là Huy, phụ trách mảng DevOps và Testing. Bây giờ em xin phép Demo thực tế hệ thống đang chạy. Thầy/Cô có thể nhìn lên màn hình:"*
> 
> **(Hành động 1 - Chạy Docker):** *"Đầu tiên, em gõ lệnh `docker-compose ps`, Thầy/Cô thấy Container B6 và Database đang chạy rất ổn định (Up)."*
> 
> **(Hành động 2 - Check Health):** *"Em mở trình duyệt truy cập `GET /health`, hệ thống trả về 200 OK báo hiệu API Gateway đang sống."*
> 
> **(Hành động 3 - Chạy Postman):** *"Đây là kịch bản test trên Postman em đã soạn sẵn. Em sẽ bấm Send giả lập một người quẹt thẻ Spam 2 lần liên tiếp. Thầy/Cô xem kết quả trả về lập tức bị chặn..."*
> 
> **(Hành động 4 - Mở Log):** *"Cuối cùng, em mở Terminal hiển thị Log của B6 (`docker-compose logs`). Đây ạ, hệ thống đã in ra cảnh báo đỏ (CRITICAL) và log cũng ghi nhận đã kết nối thành công để bắn tín hiệu báo động sang nhóm B7."*

**Lời kết (Thi chốt lại):**
> *"Dạ, phần demo luồng chạy hệ thống của nhóm 13 đến đây là kết thúc. Chúng em đã tuân thủ 100% các tiêu chí về Docker, OpenAPI và tích hợp chéo. Chúng em xin cảm ơn Thầy/Cô đã lắng nghe và xin mời Thầy/Cô đặt câu hỏi phản biện ạ!"*
