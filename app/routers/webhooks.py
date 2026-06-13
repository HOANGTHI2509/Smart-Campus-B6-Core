"""
Router: Inbound Webhook APIs
Chịu trách nhiệm hứng dữ liệu từ các phân hệ bên ngoài gửi về B6.

- POST /api/v1/webhooks/iot-event  → Nhận sự kiện từ B1 (IoT Ingestion / RFID)
- POST /api/v1/webhooks/tailgating → Nhận cảnh báo bám đuôi từ B4 (AI Vision)
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select

from app.core.dependencies import get_session
from app.models.core_models import User, Device, AccessLog
from app.schemas.webhook_schemas import (
    SensorEventPayload,
    SensorEventResponse,
    TailgatingWebhookPayload,
    WebhookResponse,
)
from app.services import outbound_api

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["Webhooks (B1 & B4 Inbound)"]
)


# ===========================================================
# WEBHOOK 1: Nhận dữ liệu từ B1 (IoT Ingestion / RFID)
# ===========================================================

@router.post(
    "/iot-event",
    response_model=SensorEventResponse,
    summary="[B1 → B6] Nhận sự kiện IoT/RFID từ phân hệ B1",
    description=(
        "Endpoint nhận sự kiện bất đồng bộ từ hệ thống IoT Ingestion (B1). "
        "Hỗ trợ các loại sự kiện: quẹt thẻ RFID, vượt ngưỡng cảm biến, "
        "thay đổi trạng thái thiết bị. "
        "Dữ liệu được xử lý và chuyển vào hàm nghiệp vụ cốt lõi."
    )
)
async def receive_iot_event(
    payload: SensorEventPayload,
    session: Session = Depends(get_session)
) -> SensorEventResponse:
    """
    Hứng dữ liệu từ B1 (IoT Ingestion) và truyền vào hàm xử lý nghiệp vụ.
    """
    logger.info(
        f"[B1→B6] Nhận sự kiện IoT | eventType={payload.eventType} "
        f"| deviceId={payload.deviceId} | correlationId={payload.correlationId}"
    )

    try:
        # --- Xử lý theo từng loại sự kiện ---

        if payload.eventType == "sensor.reading.created":
            # Sự kiện cảm biến đọc giá trị thường (bao gồm RFID/quẹt thẻ)
            return await _handle_rfid_event(payload, session)

        elif payload.eventType == "sensor.threshold.exceeded":
            # Cảm biến vượt ngưỡng → Cảnh báo
            return await _handle_threshold_exceeded(payload, session)

        elif payload.eventType == "device.status.changed":
            # Thiết bị thay đổi trạng thái (online/offline)
            return _handle_device_status_changed(payload, session)

        else:
            logger.warning(f"[B1→B6] Loại sự kiện không xác định: {payload.eventType}")
            return SensorEventResponse(
                status="ignored",
                message=f"Loại sự kiện '{payload.eventType}' không được xử lý.",
                correlationId=payload.correlationId
            )

    except Exception as exc:
        logger.error(f"[B1→B6] Lỗi khi xử lý sự kiện IoT: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xử lý sự kiện từ B1: {str(exc)}"
        )


async def _handle_rfid_event(
    payload: SensorEventPayload,
    session: Session
) -> SensorEventResponse:
    """
    Xử lý sự kiện quẹt thẻ RFID từ B1.
    Tra cứu User theo card_uid, kiểm tra hợp lệ và ghi log.
    """
    if not payload.card_uid:
        # Không phải sự kiện RFID, bỏ qua
        return SensorEventResponse(
            status="ignored",
            message="Sự kiện cảm biến thường (không phải RFID) - bỏ qua.",
            correlationId=payload.correlationId
        )

    logger.info(f"[B1→B6] Xử lý quẹt thẻ RFID | card_uid={payload.card_uid}")

    # Tra cứu User theo card_uid
    user = session.exec(
        select(User).where(User.card_uid == payload.card_uid)
    ).first()

    if not user:
        logger.warning(f"[B1→B6] Thẻ không tồn tại: {payload.card_uid}")
        # Ghi log thất bại
        _log_access_from_b1(
            session=session,
            user_id=None,
            device_id_str=payload.deviceId,
            result="failed",
            reason=f"[B1] Thẻ RFID không tồn tại: {payload.card_uid}"
        )
        return SensorEventResponse(
            status="error",
            message="Thẻ RFID chưa được đăng ký trong hệ thống.",
            correlationId=payload.correlationId
        )

    if not user.is_active:
        logger.warning(f"[B1→B6] Thẻ bị khóa | user={user.student_id}")
        _log_access_from_b1(
            session=session,
            user_id=user.id,
            device_id_str=payload.deviceId,
            result="failed",
            reason=f"[B1] Tài khoản {user.student_id} đã bị khóa"
        )
        return SensorEventResponse(
            status="error",
            message=f"Tài khoản {user.full_name} đã bị khóa.",
            correlationId=payload.correlationId
        )

    # Hợp lệ → Ghi log thành công
    logger.info(f"[B1→B6] Quẹt thẻ hợp lệ | user={user.student_id} | device={payload.deviceId}")
    _log_access_from_b1(
        session=session,
        user_id=user.id,
        device_id_str=payload.deviceId,
        result="success",
        reason=f"[B1] RFID hợp lệ qua thiết bị {payload.deviceId}"
    )

    return SensorEventResponse(
        status="success",
        message=f"Sự kiện RFID của {user.full_name} đã được ghi nhận.",
        correlationId=payload.correlationId
    )


async def _handle_threshold_exceeded(
    payload: SensorEventPayload,
    session: Session
) -> SensorEventResponse:
    """
    Xử lý khi cảm biến vượt ngưỡng → Kích hoạt cảnh báo sang B7.
    """
    severity_map = {
        "LOW": "low",
        "MEDIUM": "medium",
        "HIGH": "high",
        "CRITICAL": "critical"
    }
    severity_str = severity_map.get(payload.severity or "HIGH", "high")

    alert_message = (
        f"[Cảnh báo từ B1] Cảm biến {payload.sensorType or 'unknown'} "
        f"tại {payload.locationId or payload.deviceId} "
        f"vượt ngưỡng: {payload.value} {payload.unit or ''} "
        f"(ngưỡng: {payload.threshold})"
    )

    logger.warning(f"[B1→B6] Ngưỡng cảm biến vượt mức! {alert_message}")

    # Gửi cảnh báo sang B7 (Notification)
    forwarded = await outbound_api.send_alert_b7(
        message=alert_message,
        severity=severity_str
    )

    return SensorEventResponse(
        status="success",
        message=f"Cảnh báo ngưỡng đã ghi nhận. Đã forward sang B7: {forwarded}",
        correlationId=payload.correlationId
    )


def _handle_device_status_changed(
    payload: SensorEventPayload,
    session: Session
) -> SensorEventResponse:
    """
    Ghi nhận thay đổi trạng thái thiết bị từ B1.
    """
    logger.info(
        f"[B1→B6] Thiết bị thay đổi trạng thái | deviceId={payload.deviceId}"
    )
    # Nghiệp vụ cập nhật trạng thái device có thể mở rộng tại đây
    return SensorEventResponse(
        status="success",
        message=f"Đã ghi nhận thay đổi trạng thái thiết bị {payload.deviceId}.",
        correlationId=payload.correlationId
    )


def _log_access_from_b1(
    session: Session,
    user_id,
    device_id_str: str,
    result: str,
    reason: str
):
    """Ghi AccessLog khi nhận sự kiện từ B1."""
    try:
        log = AccessLog(
            user_id=user_id,
            device_id=None,  # B1 truyền string device ID, không map trực tiếp FK
            timestamp=datetime.utcnow(),
            status=result,
            reason=reason
        )
        session.add(log)
        session.commit()
    except Exception as e:
        logger.error(f"Lỗi ghi AccessLog từ B1: {e}")


# ===========================================================
# WEBHOOK 2: Nhận cảnh báo bám đuôi từ B4 (AI Vision)
# ===========================================================

@router.post(
    "/tailgating",
    response_model=WebhookResponse,
    summary="[B4 → B6] Nhận cảnh báo bám đuôi (Tailgating) từ AI Vision",
    description=(
        "B4 (AI Vision) gọi endpoint này khi phát hiện >= 2 khuôn mặt tại cổng, "
        "dấu hiệu của hành vi bám đuôi (tailgating). "
        "B6 sẽ ghi nhận sự kiện và forward cảnh báo khẩn cấp sang B7 (Notification)."
    )
)
async def receive_tailgating_alert(
    payload: TailgatingWebhookPayload,
    session: Session = Depends(get_session)
) -> WebhookResponse:
    """
    Hứng cảnh báo tailgating từ B4 (AI Vision) và truyền xử lý.
    """
    logger.warning(
        f"[B4→B6] CẢNH BÁO BÁM ĐUÔI! | gate_id={payload.gate_id} "
        f"| faces={payload.detected_faces_count} | alert_type={payload.alert_type}"
    )

    try:
        # Xây dựng nội dung cảnh báo chi tiết
        user_info = ""
        if payload.user_ids:
            user_info = f" Danh sách nhận diện: {', '.join(payload.user_ids)}."

        alert_message = (
            f"[Cảnh báo Bám đuôi - B4] Phát hiện {payload.detected_faces_count} "
            f"người tại cổng {payload.gate_id}.{user_info}"
        )

        if payload.image_ref:
            alert_message += f" Bằng chứng: {payload.image_ref}"

        # Xác định mức độ nghiêm trọng dựa trên số khuôn mặt
        if payload.detected_faces_count >= 5:
            severity = "critical"
        elif payload.detected_faces_count >= 3:
            severity = "high"
        else:
            severity = "medium"

        logger.warning(f"[B4→B6] Gửi cảnh báo lên B7 | severity={severity}")

        # Forward cảnh báo sang B7 (Notification)
        forwarded = await outbound_api.send_alert_b7(
            message=alert_message,
            severity=severity
        )

        # Ghi AccessLog với trạng thái failed (phát hiện bất thường)
        log = AccessLog(
            user_id=None,
            device_id=None,
            timestamp=payload.timestamp or datetime.utcnow(),
            status="failed",
            reason=f"[B4] Tailgating tại cổng {payload.gate_id}: {payload.detected_faces_count} khuôn mặt"
        )
        session.add(log)
        session.commit()

        return WebhookResponse(
            received=True,
            message=f"Cảnh báo bám đuôi tại cổng {payload.gate_id} đã được ghi nhận.",
            alert_forwarded=forwarded
        )

    except Exception as exc:
        logger.error(f"[B4→B6] Lỗi xử lý cảnh báo tailgating: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xử lý cảnh báo tailgating: {str(exc)}"
        )
