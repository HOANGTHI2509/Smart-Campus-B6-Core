import paho.mqtt.client as mqtt
import json
import logging
import time
import csv
import os
import threading
import datetime
from app.core.config import settings
from app.services.logger_store import add_log
from app.core.database import SessionLocal, EnvironmentLog

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

# TRẠNG THÁI SENSOR FUSION & RATE LIMITING
# room -> {device_id, timestamp, payload, b4_confirmed, b4_risk_level, b4_payload}
pending_fire_alerts = {}
pending_lock = threading.Lock()

# room -> timestamp of recent B4 fire alert
recent_b4_fire_alerts = {}
recent_b4_lock = threading.Lock()

# device_id -> timestamp of last B7 outbound call
last_alert_times = {}
last_alert_lock = threading.Lock()


def get_room_from_device(device_id: str) -> str:
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "IoT_device_registry.csv")
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("device_id") == device_id:
                        return row.get("room", "")
        except Exception as e:
            logger.error(f"Error reading IoT_device_registry.csv: {e}")
    
    # Fallback mappings
    device_lower = device_id.lower()
    if "a101" in device_lower:
        return "A101"
    if "a102" in device_lower:
        return "A102"
    if "gate-a" in device_lower:
        return "GATE-A"
    if "library" in device_lower or "lib" in device_lower:
        return "LIB-01"
    if "b201" in device_lower:
        return "B201"
    return "Unknown"


def get_room_from_camera(camera_id: str) -> str:
    camera_lower = camera_id.lower()
    if "a101" in camera_lower:
        return "A101"
    if "a102" in camera_lower:
        return "A102"
    if "gate" in camera_lower or "cổng" in camera_lower:
        return "GATE-A"
    if "lib" in camera_lower or "thư viện" in camera_lower:
        return "LIB-01"
    if "b201" in camera_lower:
        return "B201"
    return "Unknown"


def register_b4_fire_alert(camera_id: str, payload_dict: dict):
    room = get_room_from_camera(camera_id)
    current_time = time.time()
    
    with recent_b4_lock:
        recent_b4_fire_alerts[room] = current_time
        
    with pending_lock:
        if room in pending_fire_alerts:
            logger.info(f"🎯 [SENSOR FUSION] B4 xác nhận có lửa tại phòng {room} (Camera {camera_id})!")
            pending_fire_alerts[room]["b4_confirmed"] = True
            pending_fire_alerts[room]["b4_risk_level"] = payload_dict.get("riskLevel")
            pending_fire_alerts[room]["b4_payload"] = payload_dict


def check_and_send_b7_alert(device_id: str, title: str, level: str, message: str, payload: dict):
    """
    Kiểm tra rate limiting 60s cho device_id.
    Nếu OK: thực hiện gọi B7, cập nhật thời gian.
    Nếu bị chặn: chỉ ghi log (console + add_log), không gọi B7.
    """
    current_time = time.time()
    with last_alert_lock:
        last_time = last_alert_times.get(device_id, 0.0)
        cooldown_remaining = 60.0 - (current_time - last_time)
        if cooldown_remaining > 0:
            logger.info(f"⏳ [RATE LIMIT] Bỏ qua gửi báo động B7 cho thiết bị {device_id} (Còn lại {cooldown_remaining:.1f}s Cooldown). Message: {message}")
            add_log("INFO", f"[COOLDOWN SPAM] Bỏ qua gọi B7 cho {device_id} (Còn {cooldown_remaining:.1f}s): {message}", "B1_IOT_SENSOR", payload)
            return
        last_alert_times[device_id] = current_time

    url_b7 = f"{settings.B7_NOTIFICATION_URL}/notify/send"
    logger.info(f"🚀 [OUTBOUND] Đang gửi lệnh BÁO ĐỘNG ({level}) sang B7: {url_b7}")
    try:
        import httpx
        resp = httpx.post(url_b7, json={"title": title, "level": level, "message": message}, timeout=5.0)
        if resp.status_code in [200, 201]:
            logger.info("✅ [THÀNH CÔNG] Nhóm B7 đã nhận lệnh báo động!")
        else:
            logger.error(f"❌ [LỖI B7] Nhóm B7 phản hồi status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"❌ [LỖI OUTBOUND B7] B7 đang sập hoặc lỗi mạng LAN: {e}")


def process_fire_decision(room: str, device_id: str, payload: dict):
    """
    Đợi 5 giây để gom dữ liệu B4 và đưa ra quyết định cảnh báo hỏa hoạn.
    """
    logger.info(f"⏳ [SENSOR FUSION] B1 báo cháy tại {room} ({device_id}). Đang giữ cảnh báo 5 giây để chờ B4 AI Vision xác nhận...")
    time.sleep(5.0)
    
    with pending_lock:
        alert_data = pending_fire_alerts.pop(room, None)
        
    if not alert_data:
        return
        
    b4_confirmed = alert_data.get("b4_confirmed", False)
    reason = payload.get("reason", "không rõ nguyên nhân")
    
    if b4_confirmed:
        # B1 + B4 -> CRITICAL
        msg = f"HỎA HOẠN XÁC THỰC tại {room}! B1 ({device_id}) phát hiện chỉ số cao & B4 AI Vision xác nhận có cháy! (Lý do: {reason})"
        logger.critical(f"🔥 {msg}")
        add_log("CRITICAL", msg, "SENSOR_FUSION", payload)
        check_and_send_b7_alert(
            device_id=device_id,
            title="CẢNH BÁO HỎA HOẠN CRITICAL",
            level="CRITICAL",
            message=msg,
            payload=payload
        )
    else:
        # B1 only -> WARNING (Nghi ngờ báo giả)
        msg = f"Nghi ngờ báo cháy giả tại {room}! Cảm biến B1 ({device_id}) báo cháy nhưng B4 AI Vision không phát hiện lửa. (Lý do: {reason})"
        logger.warning(f"⚠️ {msg}")
        add_log("WARNING", msg, "SENSOR_FUSION", payload)
        check_and_send_b7_alert(
            device_id=device_id,
            title="CẢNH BÁO BÁO CHÁY GIẢ / WARNING",
            level="WARNING",
            message=msg,
            payload=payload
        )


def load_rules():
    default_rules = {"Max_Temperature": 50.0, "Max_Smoke": 1.0}
    try:
        rules_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app", "core", "rules.json")
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading rules: {e}")
    return default_rules


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
    
    # Task 2: Rule Engine
    rules = load_rules()
    max_temp = rules.get("Max_Temperature", 50.0)
    max_smoke = rules.get("Max_Smoke", 1.0)
    
    threshold_exceeded = False
    reasons = []
    
    if temperature is not None:
        try:
            temp_val = float(temperature)
            if temp_val > max_temp:
                threshold_exceeded = True
                reasons.append(f"nhiệt độ {temp_val}°C vượt ngưỡng {max_temp}°C")
        except (ValueError, TypeError):
            pass
            
    if smoke is not None:
        try:
            smoke_val = float(smoke)
            if smoke_val > max_smoke:
                threshold_exceeded = True
                reasons.append(f"khói {smoke_val} ppm vượt ngưỡng {max_smoke} ppm")
        except (ValueError, TypeError):
            pass

    if threshold_exceeded:
        is_emergency = True
        override_msg = " | ".join(reasons)
        payload["reason"] = f"{payload.get('reason') or 'vượt ngưỡng cảm biến'} ({override_msg})"

    # Phân loại rõ ràng: "danger" là cháy, còn "invalid_device" là thiết bị lạ
    if status == "danger":
        is_emergency = True
    elif status == "invalid_device":
        is_security_alert = True
    elif not threshold_exceeded and status in ["normal", "sensor_error"]:
        add_log("INFO", f"[{device_id}] Nhận dữ liệu Sensor ({status})", "B1_IOT_SENSOR", payload)

    # ĐIỀU PHỐI (ORCHESTRATION) - NGUYÊN TẮC CỐT LÕI CỦA B6
    if is_emergency:
        reason = payload.get("reason", "không rõ nguyên nhân")
        room = get_room_from_device(device_id)
        
        # SENSOR FUSION logic
        b4_already_confirmed = False
        with recent_b4_lock:
            b4_time = recent_b4_fire_alerts.get(room, 0.0)
            if time.time() - b4_time <= 5.0:
                b4_already_confirmed = True

        if b4_already_confirmed:
            logger.info(f"🎯 [SENSOR FUSION] B4 đã xác nhận có lửa trước đó tại {room}! Không cần chờ 5 giây.")
            msg = f"HỎA HOẠN XÁC THỰC tại {room}! B1 ({device_id}) phát hiện chỉ số cao & B4 AI Vision đã xác nhận có cháy! (Lý do: {reason})"
            logger.critical(f"🔥 {msg}")
            add_log("CRITICAL", msg, "SENSOR_FUSION", payload)
            check_and_send_b7_alert(
                device_id=device_id,
                title="CẢNH BÁO HỎA HOẠN CRITICAL",
                level="CRITICAL",
                message=msg,
                payload=payload
            )
        else:
            with pending_lock:
                pending_fire_alerts[room] = {
                    "device_id": device_id,
                    "timestamp": time.time(),
                    "payload": payload,
                    "b4_confirmed": False
                }
            threading.Thread(target=process_fire_decision, args=(room, device_id, payload), daemon=True).start()
            
    elif is_security_alert:
        logger.warning(f"🚨 CẢNH BÁO AN NINH! Thiết bị lạ không xác định ({device_id}) đang gửi dữ liệu.")
        add_log("WARNING", f"Thiết bị lạ '{device_id}' xâm nhập mạng IoT", "B1_IOT_SENSOR", payload)
        
        # Gửi cảnh báo B7 với Rate Limiting
        check_and_send_b7_alert(
            device_id=device_id,
            title="CẢNH BÁO IOT XÂM NHẬP",
            level="WARNING",
            message=f"Thiết bị lạ '{device_id}' xâm nhập mạng IoT!",
            payload=payload
        )

    # Task 3: Database Persistence
    db = SessionLocal()
    try:
        new_log = EnvironmentLog(
            device_id=device_id,
            temperature=temperature,
            humidity=payload.get("humidity_pct") or payload.get("humidity"),
            co2=payload.get("co2_ppm") or payload.get("co2"),
            smoke=smoke,
            status=status,
            raw_payload=json.dumps(payload)
        )
        
        raw_ts = payload.get("timestamp")
        if raw_ts:
            try:
                if raw_ts.endswith("Z"):
                    raw_ts = raw_ts[:-1]
                new_log.timestamp = datetime.datetime.fromisoformat(raw_ts)
            except Exception:
                new_log.timestamp = datetime.datetime.utcnow()
        else:
            new_log.timestamp = datetime.datetime.utcnow()

        db.add(new_log)
        db.commit()
        logger.info(f"💾 Đã lưu EnvironmentLog cho {device_id} vào Database.")
    except Exception as db_err:
        logger.error(f"Lỗi khi lưu DB EnvironmentLog: {db_err}")
        db.rollback()
    finally:
        db.close()


def handle_camera_event(payload: dict):
    """
    Lắng nghe event nhẹ (lightweight) từ B2 bắn qua MQTT khi có chuyển động.
    """
    camera_id = payload.get("camera_id")
    motion = payload.get("motion_detected")
    
    if motion:
        logger.warning(f"🚶 CAMERA ALERT: Phát hiện có người chuyển động tại {camera_id}")
        add_log("WARNING", f"Phát hiện chuyển động lạ tại {camera_id}", "B2_CAMERA", payload)

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
