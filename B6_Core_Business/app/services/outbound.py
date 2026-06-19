import httpx
from app.core.config import settings

class OutboundClient:
    def __init__(self):
        # Đặt timeout = 5 giây để nếu máy nhóm khác bị sập/tắt ngang, 
        # máy B6 của mình không bị treo theo.
        self.timeout = 5.0

    async def call_b4_face_match(self, camera_id: str, image_ref: str, timestamp: str) -> dict:
        """Gọi API đối sánh khuôn mặt của nhóm AI Vision (B4)"""
        url = f"{settings.B4_AI_VISION_URL}/vision/face-match"
        payload = {
            "cameraId": camera_id,
            "imageRef": image_ref,
            "timestamp": timestamp
        }
        
        print(f"🚀 [OUTBOUND] Đang gửi yêu cầu đối sánh khuôn mặt sang B4 tại: {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status() # Báo lỗi nếu B4 trả về lỗi 500
                return response.json()
        except Exception as e:
            print(f"❌ [LỖI OUTBOUND B4] Không thể gọi nhóm AI: {e}")
            return {"faceMatched": False, "error": str(e)}

    async def call_b7_notify(self, type: str, severity: str, message: str) -> bool:
        """Gọi API phát thông báo báo động của nhóm Notification (B7)"""
        url = f"{settings.B7_NOTIFICATION_URL}/notify/send"
        
        # CHÚ Ý: B7 đang dùng schema NotifyRequest gồm title, level, message.
        # Chúng ta phải map lại type -> title và severity -> level cho đúng hợp đồng của B7
        payload = {
            "title": f"CẢNH BÁO: {type.upper()}",
            "level": severity.upper(),
            "message": message
        }
        
        print(f"🚀 [OUTBOUND] Đang gửi lệnh BÁO ĐỘNG sang B7 tại: {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                print("✅ [THÀNH CÔNG] Nhóm B7 đã nhận lệnh và đang phát chuông!")
                return True
        except Exception as e:
            print(f"❌ [LỖI OUTBOUND B7] B7 đang sập hoặc lỗi mạng LAN: {e}")
            return False

    async def call_b3_gate_command(self, command: str, uid: str) -> bool:
        """Gọi API điều khiển cổng vật lý của nhóm Access Gate (B3)"""
        url = f"{settings.B3_ACCESS_GATE_URL}/gate/command"
        payload = {
            "command": command, # Lệnh truyền vào, ví dụ "OPEN" hoặc "CLOSE"
            "uid": uid
        }
        
        print(f"🚀 [OUTBOUND] Ra lệnh {command} cho Cổng B3 tại: {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                print("✅ [THÀNH CÔNG] Nhóm B3 đã thực thi lệnh cổng!")
                return True
        except Exception as e:
            print(f"❌ [LỖI OUTBOUND B3] Không gọi được cổng B3: {e}")
            return False

    async def call_b5_analytics_export(self, from_date: str, to_date: str, data: list) -> bool:
        """Gọi API xuất dữ liệu thô (Log) sang cho nhóm B5 Analytics để vẽ biểu đồ"""
        url = f"{settings.B5_ANALYTICS_URL}/analytics/export"
        payload = {
            "from": from_date,
            "to": to_date,
            "data": data
        }
        
        print(f"🚀 [OUTBOUND] Đang xuất dữ liệu Log sang B5 tại: {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                print("✅ [THÀNH CÔNG] Nhóm B5 đã nhận được dữ liệu Analytics!")
                return True
        except Exception as e:
            print(f"❌ [LỖI OUTBOUND B5] Lỗi kết nối đến B5: {e}")
            return False

# Khởi tạo object để import ở nơi khác
outbound_client = OutboundClient()
