import paho.mqtt.client as mqtt
import json
import logging
from app.core.config import settings
from app.services.logger_store import add_log

# Cấu hình logging để in ra Terminal đẹp như cũ
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-7s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
# Tắt log rác của thư viện gọi API
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Callback khi kết nối thành công tới Broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Đã kết nối thành công tới HiveMQ Cloud: {settings.MQTT_BROKER_URL}")
        add_log("SUCCESS", "Đã kết nối thành công tới HiveMQ Cloud", "MQTT_BROKER")
        
        # Subscribe vào 2 topic chính theo hợp đồng
        client.subscribe("smart-campus/events/sensor")
        client.subscribe("smart-campus/events/camera")
    else:
        logger.error(f"Kết nối MQTT thất bại với mã lỗi: {rc}")

# Callback khi nhận được tin nhắn từ Topic đã subscribe
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        topic = msg.topic
        
        # Phục hồi nguyên bản câu lệnh in log ra màn hình Terminal như cũ của bạn!
        logger.info(f"📥 NHẬN DATA TỪ TOPIC: {topic}")
        logger.debug(f"Nội dung JSON:\n{json.dumps(payload, indent=2)}")

        if topic == "smart-campus/events/sensor":
            handle_sensor_data(topic, payload)
            
        elif topic == "smart-campus/events/camera":
            handle_camera_event(payload)

    except json.JSONDecodeError:
        logger.error(f"Lỗi format JSON từ topic {msg.topic}: {msg.payload}")
    except Exception as e:
        logger.error(f"Lỗi khi xử lý MQTT message: {str(e)}")

def handle_sensor_data(topic: str, payload: dict):
    """
    Xử lý dữ liệu thô từ B1 (IoT Ingestion).
    Payload tuân thủ Contract: B1_IoT_Ingestion_Hop_Dong_Tich_Hop.md
    """
    device_id = payload.get("device_id", "unknown")
    status = payload.get("status", "normal")
    
    # Đọc dữ liệu từ JSON phẳng theo đúng Hợp đồng của B1
    temperature = payload.get("temperature_c")
    smoke = payload.get("smoke_ppm")

    # LOGIC NGHIỆP VỤ B6 (CORE BUSINESS POLICY ENGINE)
    is_emergency = False
    is_security_alert = False
    
    # Phân loại rõ ràng: "danger" là cháy, còn "invalid_device" là thiết bị lạ
    if status == "danger":
        # CHUẨN MICROSERVICES (SINGLE RESPONSIBILITY)
        # B6 hoàn toàn tin tưởng vào "quyết định" của nhóm B1. 
        # B6 không check lại nhiệt độ, B1 hô cháy là B6 chạy điều phối sơ tán!
        is_emergency = True
    elif status == "invalid_device":
        is_security_alert = True
    elif status in ["normal", "sensor_error"]:
        add_log("INFO", f"[{device_id}] Nhận dữ liệu Sensor ({status})", "MQTT_SENSOR", payload)

    # ĐIỀU PHỐI (ORCHESTRATION) - NGUYÊN TẮC CỐT LÕI CỦA B6
    if is_emergency:
        reason = payload.get("reason", "không rõ nguyên nhân")
        logger.critical(f"🔥 KHẨN CẤP! B1 báo cháy tại {device_id}! (Lý do: {reason})")
        add_log("CRITICAL", f"B1 kích hoạt HỎA HOẠN tại {device_id} (Lý do của B1: {reason})", "MQTT_SENSOR", payload)
        
        # Hành động 1: Gọi nhóm B7 (Notification) rú còi
        url_b7 = f"{settings.B7_NOTIFICATION_URL}/notify/send"
        logger.info(f"Đang gửi API kích hoạt còi báo động tới B7: {url_b7}")
        
        # Hành động 2: Mở toàn bộ cổng B3 (Access Gate) để thoát hiểm
        url_b3 = f"{settings.B3_ACCESS_GATE_URL}/gate/control"
        logger.info(f"Đang gửi API mở tất cả cổng thoát hiểm tới B3: {url_b3}")
            
    elif is_security_alert:
        logger.warning(f"🚨 CẢNH BÁO AN NINH! Thiết bị lạ không xác định ({device_id}) đang gửi dữ liệu.")
        add_log("WARNING", f"Thiết bị lạ '{device_id}' xâm nhập mạng IoT", "MQTT_SENSOR", payload)
        
        # Hành động: Chỉ gọi nhóm B7 để thông báo cho Bảo vệ, tuyệt đối KHÔNG MỞ CỬA B3
        url_b7 = f"{settings.B7_NOTIFICATION_URL}/notify/send"
        logger.info(f"Đang gửi API báo cáo an ninh tới B7: {url_b7}")

def handle_camera_event(payload: dict):
    """
    Lắng nghe event nhẹ (lightweight) từ B2 bắn qua MQTT khi có chuyển động.
    """
    camera_id = payload.get("camera_id")
    motion = payload.get("motion_detected")
    
    if motion:
        logger.warning(f"🚶 CAMERA ALERT: Phát hiện có người chuyển động tại {camera_id}")
        add_log("WARNING", f"Phát hiện chuyển động lạ tại {camera_id}", "MQTT_CAMERA", payload)

# Khởi tạo Client MQTT
mqtt_client = mqtt.Client()

# Cấu hình tài khoản đăng nhập HiveMQ
if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
    mqtt_client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
# Dùng TLS cho kết nối an toàn (HiveMQ Cloud bắt buộc dùng TLS)
mqtt_client.tls_set()

# Gán các hàm callback
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    """Khởi động MQTT chạy ngầm (Non-blocking)"""
    if not settings.MQTT_BROKER_URL:
        logger.warning("Bỏ qua kết nối MQTT do không có cấu hình Broker")
        return
    logger.info(f"Bắt đầu kết nối MQTT tới {settings.MQTT_BROKER_URL}:{settings.MQTT_PORT}...")
    try:
        mqtt_client.connect(settings.MQTT_BROKER_URL, settings.MQTT_PORT, 60)
        mqtt_client.loop_start()  # Chạy thread ngầm
    except Exception as e:
        logger.error(f"Lỗi khởi động MQTT: {str(e)}")

def stop_mqtt():
    """Dừng MQTT an toàn khi tắt app"""
    logger.info("Đang ngắt kết nối MQTT...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
