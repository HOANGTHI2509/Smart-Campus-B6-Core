import json
import httpx
import paho.mqtt.client as mqtt
from loguru import logger
from app.core.config import settings

# Cài đặt Loguru: Ghi log ra màn hình console cực xịn, có màu sắc, và lưu file
logger.add("logs/mqtt_events.log", rotation="5 MB", encoding="utf-8")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.success("✅ [MQTT] Đã kết nối thành công tới máy chủ HiveMQ Cloud!")
        
        # TASK 2.2: Lắng nghe nhóm B1 (IoT)
        client.subscribe("smart-campus/events/sensor")
        logger.info("📡 [MQTT] Đã subscribe topic: smart-campus/events/sensor (B1 IoT)")
        
        # TASK 2.4: Lắng nghe nhóm B2 (Camera)
        client.subscribe("smart-campus/events/camera")
        logger.info("📡 [MQTT] Đã subscribe topic: smart-campus/events/camera (B2 Camera)")
    else:
        logger.error(f"❌ [MQTT] Kết nối thất bại với mã lỗi {rc}. Vui lòng check lại Password trong file .env!")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        # Giải mã chuỗi JSON nhận được
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        logger.warning(f"⚠️ [MQTT] Nhận được dữ liệu không phải JSON từ topic {topic}")
        return

    # TASK 2.5: GHI LOG ĐẸP LÀM MINH CHỨNG
    logger.info(f"📥 NHẬN DATA TỪ TOPIC: {topic}")
    logger.debug(f"Nội dung JSON:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    # Phân luồng xử lý
    if topic == "smart-campus/events/sensor":
        handle_iot_sensor_data(payload)
    elif topic == "smart-campus/events/camera":
        handle_camera_event(payload)

def handle_iot_sensor_data(payload: dict):
    """TASK 2.3: Bộ não xử lý Policy cho dữ liệu IoT"""
    device_id = payload.get("device_id", "Unknown")
    status = payload.get("status", "normal")
    alert_level = payload.get("alert_level", "info")
    
    # Lấy thông số nhiệt độ
    temperature = payload.get("data", {}).get("temperature_c", 0)

    # Logic nghiệp vụ: CẢNH BÁO NẾU CHÁY (Nhiệt > 50 hoặc status = danger)
    if status == "danger" or temperature >= 50.0:
        logger.critical(f"🔥 CẢNH BÁO IOT! Nhiệt độ siêu cao {temperature}°C tại {device_id}!")
        
        # Gọi thẳng nhóm B7 để rú còi báo cháy (Dùng httpx dạng đồng bộ)
        url = f"{settings.B7_NOTIFICATION_URL}/notify/send"
        data = {
            "title": "Báo Động Cháy Từ IoT",
            "level": "CRITICAL",
            "message": f"Thiết bị {device_id} báo nhiệt độ {temperature}°C. Yêu cầu sơ tán!"
        }
        try:
            httpx.post(url, json=data, timeout=3.0)
            logger.success("✅ Đã tự động gọi API sang nhóm B7 để bật chuông!")
        except Exception as e:
            logger.error(f"❌ Lỗi mạng khi gọi B7: {e}")

def handle_camera_event(payload: dict):
    """TASK 2.4: Xử lý sự kiện từ Camera"""
    camera_id = payload.get("cameraId", "Unknown")
    motion = payload.get("motion_detected", False)
    
    if motion:
        logger.warning(f"🚶 CAMERA ALERT: Phát hiện có người chuyển động tại {camera_id}")

# Khởi tạo Client MQTT
mqtt_client = mqtt.Client()

# Cấu hình TLS (Bắt buộc với HiveMQ Cloud)
mqtt_client.tls_set() 
# Điền User/Pass từ file config
mqtt_client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

# Gắn các hàm sự kiện
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    """Hàm bật MQTT chạy ngầm"""
    logger.info("⏳ Đang khởi động tiến trình MQTT kết nối tới HiveMQ...")
    try:
        mqtt_client.connect(settings.MQTT_BROKER_URL, settings.MQTT_PORT, 60)
        mqtt_client.loop_start() # Chạy ngầm đa luồng (Không chặn FastAPI)
    except Exception as e:
        logger.error(f"❌ Lỗi khởi động MQTT: {e}")

def stop_mqtt():
    """Hàm tắt MQTT an toàn"""
    logger.info("🛑 Đang ngắt kết nối MQTT...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
