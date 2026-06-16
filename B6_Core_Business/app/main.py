from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os
import uvicorn

from app.core.config import settings
from app.schemas.integration import DetectionResult, AccessCheckRequest
from app.services.outbound import outbound_client
from app.services.mqtt_client import start_mqtt, stop_mqtt
from app.services.logger_store import add_log, get_dashboard_payload

app = FastAPI(
    title="Smart Campus - Core Business B6",
    description="API Gateway (FastAPI) cho nhóm B6",
    version="1.0.0"
)

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
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/ai/events", tags=["webhooks"])
async def receive_vision_alert(payload: DetectionResult):
    print(f"\n[BÁO ĐỘNG] Nhận cảnh báo từ B4 AI Vision! Mức độ rủi ro: {payload.riskLevel}")
    
    # Xử lý logic nghiệp vụ: Nếu CRITICAL thì gọi sang B7
    if payload.riskLevel in ["HIGH", "CRITICAL"]:
        print(">> Đang kích hoạt module Outbound gọi nhóm B7 để bật chuông báo cháy...")
        message = f"Hệ thống phát hiện rủi ro {payload.riskLevel} tại Camera {payload.cameraId}!"
        add_log("CRITICAL", f"AI VISION BÁO ĐỘNG: {message}", "API_WEBHOOK", payload.dict())
        
        # GỌI API SANG NHÓM B7 (Outbound Task 1.6)
        await outbound_client.call_b7_notify(title="Cảnh báo an ninh", level=payload.riskLevel, message=message)

    return {"message": "Alert received and processed successfully by Core B6"}

@app.post("/access/check", tags=["access-gate"])
async def handle_gate_scan(request: AccessCheckRequest):
    print(f"\n[CỔNG {request.gateId}] Có người quẹt thẻ mã UID: {request.uid}")
    
    # Task 3.3 (Của Thành viên 3): Kiểm tra DB xem thẻ có hợp lệ không
    # Giả lập logic (Mock) tạm thời:
    is_valid_card = True if request.uid.startswith("04:A1") else False
    
    if is_valid_card:
        print(">> Thẻ Hợp Lệ! Ra lệnh MỞ CỬA.")
        add_log("SUCCESS", f"Mở cổng cho Sinh viên quẹt thẻ (UID: {request.uid})", "API_GATE", request.dict())
        # GỌI API SANG NHÓM B3 BẢO HỌ MỞ CỬA (Outbound Task 1.6)
        await outbound_client.call_b3_gate_command(command="OPEN", uid=request.uid)
        return {"allowed": True, "reason": "Access granted", "studentId": "SV001"}
    else:
        print(">> Thẻ LẠ! Ra lệnh KHÔNG MỞ.")
        add_log("WARNING", f"Từ chối mở cổng cho thẻ lạ UID: {request.uid}", "API_GATE", request.dict())
        return {"allowed": False, "reason": "Invalid UID"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.API_PORT, reload=True)
