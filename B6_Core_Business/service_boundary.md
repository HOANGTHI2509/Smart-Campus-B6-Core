# Service Boundaries - Giới Hạn Của B6

Tài liệu này xác định rõ trách nhiệm (Responsibility) và giới hạn nghiệp vụ (Boundary) của dịch vụ **B6 Core Business**, tuân thủ nghiêm ngặt nguyên tắc Single Responsibility trong kiến trúc Microservices.

## 1. Trách nhiệm Cốt lõi (In-Boundary)
- **Đánh giá rủi ro an ninh/môi trường:** Dựa trên các thông điệp cảnh báo từ hệ thống AI Vision (B4) và IoT (B1). B6 không phân tích ảnh hay cảm biến thô, mà tin tưởng 100% vào phân tích của B1 và B4.
- **Điều phối phản ứng khẩn cấp:** Quyết định kích hoạt còi báo động (tới B7) và mở toàn bộ cổng thoát hiểm (tới B3) khi có hỏa hoạn.
- **Kiểm soát truy cập (Access Control):** Xác thực định danh người dùng dựa trên UID thẻ từ nhóm B3, đối chiếu với Whitelist Database để cấp hoặc từ chối quyền mở cửa.
- **Quản lý Log giám sát:** Lưu trữ tạm thời trạng thái hệ thống vào RAM để phục vụ Web Dashboard thời gian thực.

## 2. Nằm ngoài giới hạn (Out-of-Boundary)
- **Xử lý dữ liệu thô:** B6 KHÔNG giao tiếp trực tiếp với phần cứng. B6 không đo nhiệt độ, không tự xử lý frame ảnh camera (Nhiệm vụ của B1, B2).
- **Lưu trữ Log lâu dài:** B6 chỉ phục vụ Real-time Dashboard, việc lưu trữ Data Warehouse và phân tích chuyên sâu thuộc về nhóm Analytics (B5).
- **Trực tiếp điều khiển thiết bị:** B6 không đóng mở dòng điện của cổng hay hú còi vật lý, mà chỉ gửi tín hiệu `HTTP POST` qua cho B3 và B7 thực thi.
- **Nhận diện khuôn mặt:** B6 không so khớp khuôn mặt sinh viên, B6 gọi sang B4 để nhờ B4 so khớp.
