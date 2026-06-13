from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract
from sqlmodel import Session, select

from app.core.dependencies import get_current_user, get_session
from app.models.core_models import AccessLog, Device, Role, User
from app.schemas.analytics_schemas import AccessLogAnalyticsResponse


router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics (Nhom B5)"])


@router.get("/access-logs", response_model=list[AccessLogAnalyticsResponse])
def get_access_logs(
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    start_hour: Optional[int] = Query(default=None, ge=0, le=23),
    end_hour: Optional[int] = Query(default=None, ge=0, le=23),
    building: Optional[str] = Query(default=None),
    user_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(AccessLog, User, Device, Role)
        .select_from(AccessLog)
        .join(User, AccessLog.user_id == User.id, isouter=True)
        .join(Device, AccessLog.device_id == Device.id, isouter=True)
        .join(Role, User.role_id == Role.id, isouter=True)
        .order_by(AccessLog.timestamp.desc())
    )

    if start_date:
        statement = statement.where(AccessLog.timestamp >= datetime.combine(start_date, time.min))

    if end_date:
        statement = statement.where(AccessLog.timestamp <= datetime.combine(end_date, time.max))

    if start_hour is not None:
        statement = statement.where(extract("hour", AccessLog.timestamp) >= start_hour)

    if end_hour is not None:
        statement = statement.where(extract("hour", AccessLog.timestamp) <= end_hour)

    if building:
        statement = statement.where(Device.device_name.ilike(f"%{building}%"))

    if user_type:
        statement = statement.where(Role.role_name == user_type)

    if status:
        statement = statement.where(AccessLog.status == status)

    rows = session.exec(statement).all()

    return [
        AccessLogAnalyticsResponse(
            id=access_log.id,
            timestamp=access_log.timestamp,
            access_date=access_log.timestamp.date(),
            access_hour=access_log.timestamp.hour,
            status=access_log.status,
            reason=access_log.reason,
            user_id=user.id if user else None,
            user_name=user.full_name if user else None,
            student_id=user.student_id if user else None,
            user_type=role.role_name if role else None,
            device_id=device.id if device else None,
            device_name=device.device_name if device else None,
            device_type=device.device_type if device else None,
        )
        for access_log, user, device, role in rows
    ]
