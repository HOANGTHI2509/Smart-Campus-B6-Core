from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import datetime, timedelta
from jose import jwt

from app.models.core_models import Device, User
from app.schemas.access_schemas import AccessCheckRequest, AccessCheckResponse, Token
from app.core.dependencies import get_session, SECRET_KEY, ALGORITHM
from app.services.access_service import AccessService

# Tao router rieng cho nhom giao tiep voi Cong B3
router = APIRouter(prefix="/api/v1/access", tags=["Access Control (Nhom B3)"])

# API: Kiem tra the tu de mo cong
@router.post("/check", response_model=AccessCheckResponse)
def check_access(request: AccessCheckRequest, session: Session = Depends(get_session)):
    device = _find_device(session, request.gate_id)
    if not device:
        return AccessCheckResponse(
            status="error",
            is_granted=False,
            message="Gate device not found in system!"
        )

    access_service = AccessService(session)
    is_granted, reason, user = access_service.verify_access(request.card_uid, device.id)

    if not is_granted:
        return AccessCheckResponse(
            status="error",
            is_granted=False,
            message=reason,
            user_name=user.full_name if user else None
        )

    return AccessCheckResponse(
        status="success",
        is_granted=True,
        message="Xac thuc thanh cong. Xin moi qua cong!",
        user_name=user.full_name if user else None
    )


def _find_device(session: Session, gate_id: str) -> Device | None:
    if gate_id.isdigit():
        device = session.get(Device, int(gate_id))
        if device:
            return device

    statement = select(Device).where(Device.device_name == gate_id)
    return session.exec(statement).first()


# API: Dang nhap sinh vien de lay JWT Token
@router.post("/login", response_model=Token, tags=["Authentication"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    # Su dung student_id lam username trong OAuth2
    statement = select(User).where(User.student_id == form_data.username)
    user = session.exec(statement).first()

    # O phien ban Lab 04 nay tam thoi chua bam mat khau, co the dung card_uid lam password hoac bo qua
    # Thuc te nen dung passlib de verify password
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tai khoan hoac mat khau khong dung",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Tao token payload
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode = {"sub": user.student_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": encoded_jwt, "token_type": "bearer"}
