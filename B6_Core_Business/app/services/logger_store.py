import datetime
import threading
import httpx
import time
from app.core.config import settings

system_logs = []
metrics = {
    "total_events": 0,
    "critical_alerts": 0
}

service_status = {
    "b3": "Đang kiểm tra...",
    "b4": "Đang kiểm tra...",
    "b5": "Đang kiểm tra...",
    "b7": "Đang kiểm tra..."
}

def ping_services():
    while True:
        try:
            httpx.get(settings.B3_ACCESS_GATE_URL, timeout=1.0)
            service_status["b3"] = "Đã kết nối LAN"
        except:
            service_status["b3"] = "Mất kết nối LAN"
            
        try:
            # B4 có endpoint /health trong hợp đồng
            httpx.get(f"{settings.B4_AI_VISION_URL}/health", timeout=1.0)
            service_status["b4"] = "Đã kết nối LAN"
        except:
            service_status["b4"] = "Mất kết nối LAN"
            
        try:
            httpx.get(settings.B5_ANALYTICS_URL, timeout=1.0)
            service_status["b5"] = "Đã kết nối LAN"
        except:
            service_status["b5"] = "Mất kết nối LAN"
            
        try:
            httpx.get(settings.B7_NOTIFICATION_URL, timeout=1.0)
            service_status["b7"] = "Đã kết nối LAN"
        except:
            service_status["b7"] = "Mất kết nối LAN"
            
        time.sleep(5)

# Khởi chạy luồng chạy ngầm để ping liên tục
threading.Thread(target=ping_services, daemon=True).start()

def add_log(level: str, message: str, source: str = "SYSTEM", payload: dict = None, status_code: int = 200):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "level": level,
        "source": source,
        "message": message,
        "payload": payload,
        "status_code": status_code
    }
    system_logs.insert(0, log_entry)
    
    # Cập nhật số liệu thật
    metrics["total_events"] += 1
    if level in ["CRITICAL", "WARNING"]:
        metrics["critical_alerts"] += 1
        
    # Giữ lại 50 log mới nhất để không đầy bộ nhớ
    if len(system_logs) > 50:
        system_logs.pop()

def get_dashboard_payload():
    return {
        "status": "connected",
        "logs": system_logs,
        "metrics": metrics,
        "services": service_status
    }
