from fastapi import FastAPI
from app.core.config import settings
from app.schemas.integration import DetectionResult, AccessCheckRequest
from app.services.outbound import outbound_client
from app.services.mqtt_client import start_mqtt, stop_mqtt
import uvicorn

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

@app.post("/ai/events", tags=["webhooks"])
async def receive_vision_alert(payload: DetectionResult):
    print(f"\n🚨 [BÁO ĐỘNG] Nhận cảnh báo từ B4 AI Vision! Mức độ rủi ro: {payload.riskLevel}")
    print(f"Chi tiết Payload: {payload.model_dump_json(indent=2)}\n")
    
    # Xử lý logic nghiệp vụ: Nếu CRITICAL thì gọi sang B7
    if payload.riskLevel in ["HIGH", "CRITICAL"]:
        print(">> Đang kích hoạt module Outbound gọi nhóm B7 để bật chuông báo cháy...")
        message = f"Hệ thống phát hiện rủi ro {payload.riskLevel} tại Camera {payload.cameraId}!"
        
        # GỌI API SANG NHÓM B7 (Outbound Task 1.6)
        await outbound_client.call_b7_notify(title="Cảnh báo an ninh", level=payload.riskLevel, message=message)

    return {"message": "Alert received and processed successfully by Core B6"}

@app.post("/access/check", tags=["access-gate"])
async def handle_gate_scan(request: AccessCheckRequest):
    print(f"\n🚪 [CỔNG {request.gateId}] Có người quẹt thẻ mã UID: {request.uid}")
    
    # Task 3.3 (Của Thành viên 3): Kiểm tra DB xem thẻ có hợp lệ không
    # Giả lập logic (Mock) tạm thời:
    is_valid_card = True if request.uid.startswith("04:A1") else False
    
    if is_valid_card:
        print(">> Thẻ Hợp Lệ! Ra lệnh MỞ CỬA.")
        # GỌI API SANG NHÓM B3 BẢO HỌ MỞ CỬA (Outbound Task 1.6)
        await outbound_client.call_b3_gate_command(command="OPEN", uid=request.uid)
        return {"allowed": True, "reason": "Access granted", "studentId": "SV001"}
    else:
        print(">> Thẻ LẠ! Ra lệnh KHÔNG MỞ.")
        return {"allowed": False, "reason": "Invalid UID"}

if __name__ == "__main__":
    # Lắng nghe ở host="0.0.0.0" để máy khác trong LAN có thể chọc vào được
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.API_PORT, reload=True)
