import os
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()

# Lấy URL của B3 và B7 từ biến môi trường
B3_API_URL = os.getenv("B3_API_URL", "http://localhost:8003/api/v1/gate/open")
B7_API_URL = os.getenv("B7_API_URL", "http://localhost:8007/api/v1/alerts")

logger = logging.getLogger(__name__)

async def open_gate_b3(device_id: int) -> bool:
    """
    Gọi sang hệ thống B3 (Access Gate) để ra lệnh MỞ CỔNG.
    - device_id: ID của cổng/thiết bị cần mở.
    """
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "device_id": device_id,
                "action": "open",
                "source": "B6_Core_Business"
            }
            logger.info(f"Đang gửi lệnh mở cổng tới B3: {payload}")
            response = await client.post(B3_API_URL, json=payload, timeout=5.0)
            
            if response.status_code in (200, 201, 202):
                logger.info("✅ Lệnh mở cổng đã được B3 tiếp nhận thành công.")
                return True
            else:
                logger.error(f"❌ B3 phản hồi lỗi: {response.status_code} - {response.text}")
                return False
    except httpx.RequestError as exc:
        logger.error(f"🔥 Lỗi kết nối tới mạng của B3: {exc}")
        return False

async def send_alert_b7(message: str, severity: str = "high") -> bool:
    """
    Gọi sang hệ thống B7 (Notification) để kích hoạt cảnh báo (chuông/tin nhắn).
    - message: Nội dung cảnh báo (VD: "Phát hiện người lạ đột nhập ở Cổng A").
    - severity: Mức độ nghiêm trọng ("low", "medium", "high", "critical").
    """
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "message": message,
                "severity": severity,
                "source": "B6_Core_Business"
            }
            logger.warning(f"Đang gửi cảnh báo tới B7: {payload}")
            response = await client.post(B7_API_URL, json=payload, timeout=5.0)
            
            if response.status_code in (200, 201, 202):
                logger.info("✅ Cảnh báo đã được gửi sang B7 thành công.")
                return True
            else:
                logger.error(f"❌ B7 phản hồi lỗi: {response.status_code} - {response.text}")
                return False
    except httpx.RequestError as exc:
        logger.error(f"🔥 Lỗi kết nối tới mạng của B7: {exc}")
        return False
