from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# ============================================================
# Schema cho dữ liệu từ B1 (IoT Ingestion) - theo AsyncAPI spec
# ============================================================

class SensorEventPayload(BaseModel):
    """
    Schema nhận dữ liệu sensor/RFID từ phân hệ B1 (IoT Ingestion).
    Tuân theo hợp đồng AsyncAPI trong api-b6-b1.yaml.
    """
    eventType: Literal[
        "sensor.reading.created",
        "sensor.threshold.exceeded",
        "device.status.changed"
    ] = Field(..., description="Loại sự kiện từ thiết bị IoT")
    eventId: str = Field(..., description="UUID duy nhất của sự kiện")
    correlationId: str = Field(..., description="UUID để trace xuyên suốt hệ thống")
    deviceId: str = Field(..., description="ID thiết bị IoT gửi dữ liệu")
    locationId: Optional[str] = Field(None, description="ID vị trí của thiết bị")
    sensorType: Optional[str] = Field(None, description="Loại cảm biến (rfid, temperature, humidity...)")
    value: Optional[float] = Field(None, description="Giá trị đo được")
    unit: Optional[str] = Field(None, description="Đơn vị đo (°C, %, ...)")
    threshold: Optional[float] = Field(None, description="Ngưỡng cảnh báo")
    severity: Optional[Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]] = Field(
        None, description="Mức độ nghiêm trọng khi vượt ngưỡng"
    )
    timestamp: Optional[datetime] = Field(None, description="Thời điểm xảy ra sự kiện")
    # Trường riêng cho sự kiện RFID (card_uid)
    card_uid: Optional[str] = Field(None, description="Mã thẻ từ/RFID (nếu là sự kiện quẹt thẻ)")

    class Config:
        json_schema_extra = {
            "example": {
                "eventType": "sensor.reading.created",
                "eventId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "correlationId": "f0e1d2c3-b4a5-9687-8765-432100fedcba",
                "deviceId": "GATE-A-001",
                "locationId": "LOC-MAIN-GATE",
                "sensorType": "rfid",
                "card_uid": "A1B2C3D4",
                "timestamp": "2026-06-13T10:00:00Z"
            }
        }


class SensorEventResponse(BaseModel):
    """Phản hồi sau khi B6 xử lý sự kiện từ B1."""
    status: str = Field(..., description="success | ignored | error")
    message: str
    correlationId: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================
# Schema cho Webhook từ B4 (AI Vision) - Cảnh báo bám đuôi
# ============================================================

class TailgatingWebhookPayload(BaseModel):
    """
    Schema nhận cảnh báo bám đuôi (tailgating) từ phân hệ B4 (AI Vision).
    B4 bắn webhook về B6 khi phát hiện >= 2 khuôn mặt tại cổng.
    Tuân theo hợp đồng OpenAPI trong api-b6-b4.yaml.
    """
    gate_id: str = Field(..., description="ID cổng phát hiện bám đuôi")
    detected_faces_count: int = Field(..., ge=2, description="Số khuôn mặt phát hiện (>= 2)")
    alert_type: str = Field(default="tailgating", description="Loại cảnh báo")
    user_ids: Optional[list[str]] = Field(
        None, description="Danh sách user_id đã nhận diện được (nếu có)"
    )
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Độ tin cậy nhận diện (0.0 - 1.0)"
    )
    image_ref: Optional[str] = Field(None, description="URL ảnh/video bằng chứng")
    timestamp: Optional[datetime] = Field(None, description="Thời điểm phát hiện")

    class Config:
        json_schema_extra = {
            "example": {
                "gate_id": "GATE-A-001",
                "detected_faces_count": 2,
                "alert_type": "tailgating",
                "user_ids": ["SV001", "UNKNOWN"],
                "confidence": 0.95,
                "image_ref": "http://s3.smartcampus.local/evidence/gate-a-001-20260613.jpg",
                "timestamp": "2026-06-13T10:05:00Z"
            }
        }


class WebhookResponse(BaseModel):
    """Phản hồi chung cho các Webhook nhận từ hệ thống bên ngoài."""
    received: bool = True
    message: str
    alert_forwarded: Optional[bool] = Field(
        None, description="True nếu đã forward cảnh báo sang B7"
    )
    processed_at: datetime = Field(default_factory=datetime.utcnow)
