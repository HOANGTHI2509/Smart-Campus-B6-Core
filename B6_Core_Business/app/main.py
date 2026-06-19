from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os
import uvicorn

from app.core.config import settings
from app.schemas.integration import DetectionResult, AccessCheckRequest, CameraEvent
from app.services.outbound import outbound_client
from app.services.mqtt_client import start_mqtt, stop_mqtt
from app.services.logger_store import add_log, get_dashboard_payload
import time
from datetime import datetime

app = FastAPI(
    title="Smart Campus - Core Business B6",
    description="API Gateway (FastAPI) cho nhóm B6",
    version="1.0.0"
)

# In-memory store for rate limiting (anti-passback)
recent_swipes = {}

@app.on_event("startup")
def on_startup():
    start_mqtt()

@app.on_event("shutdown")
def on_shutdown():
    stop_mqtt()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to B6 Core Business API",
        "doc_url": "/docs"
    }

@app.get("/health", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "service": "b6-core-business",
        "version": "1.0.0"
    }

@app.get("/dashboard", response_class=HTMLResponse, tags=["ui"])
def serve_dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import json

@app.get("/api/dashboard-data", tags=["ui"])
def get_dashboard_data():
    return get_dashboard_payload()

@app.get("/api/dashboard-stream", tags=["ui"])
async def dashboard_stream():
    """Server-Sent Events (SSE) để truyền dữ liệu Real-time liên tục không cần load trang"""
    async def event_generator():
        while True:
            data = get_dashboard_payload()
            yield f"data: {json.dumps(data, default=str)}\n\n"
            await asyncio.sleep(1)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/v1/webhook/vision", tags=["webhooks"])
async def receive_vision_alert(payload: DetectionResult):
    print(f"\n[BÁO ĐỘNG B4] Nhận cảnh báo từ B4 AI Vision! Mức độ rủi ro: {payload.riskLevel}")
    
    # Xử lý logic nghiệp vụ: Nếu CRITICAL thì gọi sang B7
    if payload.riskLevel in ["HIGH", "CRITICAL"]:
        print(">> Đang kích hoạt module Outbound gọi nhóm B7 để bật chuông báo cháy...")
        message = f"Hệ thống phát hiện rủi ro {payload.riskLevel} tại Camera {payload.cameraId}!"
        add_log("CRITICAL", f"AI VISION BÁO ĐỘNG: {message}", "B4_AI_VISION", payload.dict(), status_code=201)
        # Thực hiện gọi API ra ngoài (Outbound) tới nhóm B7 Notification
        await outbound_client.call_b7_notify(type="ai_vision_alert", severity=payload.riskLevel.lower(), message=message)
    else:
        add_log("INFO", f"Nhận dạng AI bình thường tại {payload.cameraId}", "B4_AI_VISION", payload.dict(), status_code=200)

    return {"message": "Alert received and processed successfully by Core B6"}

@app.post("/camera-events", tags=["webhooks"])
async def receive_camera_event(payload: CameraEvent):
    print(f"\n[CAMERA B2] Nhận event trực tiếp từ B2 Camera Stream! Độ nguy hiểm: {payload.severity}")
    
    log_level = payload.severity if payload.severity in ["WARNING", "CRITICAL"] else "INFO"
    if payload.abnormal:
        log_level = "CRITICAL"
        add_log(log_level, f"CAMERA CẢNH BÁO: Phát hiện vật thể bất thường tại {payload.cameraId}", "B2_CAMERA", payload.dict(), status_code=201)
        await outbound_client.call_b7_notify(type="camera_anomaly", severity="critical", message=f"B2 Cảnh báo: Camera {payload.cameraId} có vật thể bất thường!")
    else:
        add_log(log_level, f"Nhận event Camera tại {payload.cameraId}", "B2_CAMERA", payload.dict(), status_code=200)

    return {"message": "Camera event processed"}

from typing import Union, List

@app.post("/api/v1/events/access", tags=["access-gate"])
async def handle_gate_scan(request: Union[AccessCheckRequest, List[AccessCheckRequest]]):
    # Nếu B3 gửi Bulk Sync (Một mảng nhiều event)
    if isinstance(request, list):
        print(f"\n[CỔNG B3] Nhận được BULK SYNC gồm {len(request)} events!")
        for req in request:
            add_log("INFO", f"Bulk Sync: Lưu lịch sử quẹt thẻ (UID: {req.uid})", "B3_ACCESS_GATE", req.dict())
        return {"message": f"Successfully processed {len(request)} bulk events"}
    
    # Nếu B3 gửi 1 event đơn lẻ
    print(f"\n[CỔNG {request.gateId}] Có người quẹt thẻ mã UID: {request.uid}")
    
    # Task 3.3: Xử lý luật nghiệp vụ (Rule Engine)
    current_time = time.time()
    last_swipe = recent_swipes.get(request.uid, 0)
    
    # Rule 1: Một thẻ quẹt quá nhiều lần trong 5 giây (Anti-passback / Rate Limiting)
    if current_time - last_swipe < 5:
        print(">> Thẻ bị quẹt liên tục! Đánh dấu bất thường.")
        add_log("WARNING", f"Quẹt thẻ quá nhanh UID: {request.uid}", "B3_ACCESS_GATE", request.dict(), status_code=429)
        await outbound_client.call_b7_notify(
            type="rate_limit_exceeded", 
            severity="medium", 
            message=f"Thẻ {request.uid} quẹt quá nhiều lần trong thời gian ngắn"
        )
        return {"allowed": False, "reason": "Rate limit exceeded. Please wait."}
    
    recent_swipes[request.uid] = current_time

    # Rule 2: Quẹt thẻ ngoài giờ cho phép (22:00 - 06:00)
    hour = datetime.now().hour
    if hour >= 22 or hour < 6:
        print(">> Quẹt thẻ ngoài giờ cho phép! Đánh dấu xâm nhập trái phép.")
        add_log("WARNING", f"Quẹt thẻ ngoài giờ UID: {request.uid}", "B3_ACCESS_GATE", request.dict(), status_code=403)
        await outbound_client.call_b7_notify(
            type="unauthorized_access", 
            severity="high", 
            message="Access attempt outside allowed time"
        )
        return {"allowed": False, "reason": "Access denied. Outside allowed hours."}
    
    # Kiểm tra thẻ trong Whitelist DB (giả lập)
    is_valid_card = True if request.uid.startswith("04:A1") else False
    
    if is_valid_card:
        print(">> Thẻ Hợp Lệ! Đã xác thực thành công (Tính năng gọi API mở cửa vật lý tạm đóng theo yêu cầu B3).")
        add_log("SUCCESS", f"Mở cổng cho Sinh viên quẹt thẻ (UID: {request.uid})", "B3_ACCESS_GATE", request.dict(), status_code=200)
        return {"allowed": True, "reason": "Access granted", "studentId": "SV001"}
    else:
        print(">> Thẻ LẠ! Ra lệnh KHÔNG MỞ và gọi còi báo động B7.")
        add_log("WARNING", f"Từ chối mở cổng cho thẻ lạ UID: {request.uid}", "B3_ACCESS_GATE", request.dict(), status_code=403)
        # Gọi sang B7 hú còi báo động vì phát hiện thẻ lạ xâm nhập
        await outbound_client.call_b7_notify(
            type="invalid_card", 
            severity="high", 
            message=f"Phát hiện có người dùng thẻ lạ chưa đăng ký (UID: {request.uid}) cố tình mở cổng!"
        )
        return {"allowed": False, "reason": "Invalid UID"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.API_PORT, reload=True)
