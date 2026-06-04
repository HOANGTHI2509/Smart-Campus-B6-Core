from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import datetime, timedelta
from jose import jwt

from app.models.core_models import User
from app.schemas.access_schemas import AccessCheckRequest, AccessCheckResponse, Token
from app.core.dependencies import get_session, SECRET_KEY, ALGORITHM
# Tạo router riêng cho nhóm giao tiếp với Cổng B3
router = APIRouter(prefix="/api/v1/access", tags=["Access Control (Nhóm B3)"])

# API: Kiểm tra thẻ từ để mở cổng
@router.post("/check", response_model=AccessCheckResponse)
def check_access(request: AccessCheckRequest, session: Session = Depends(get_session)):
    # 1. Truy vấn Database tìm sinh viên sở hữu mã thẻ này
    statement = select(User).where(User.card_uid == request.card_uid)
    user = session.exec(statement).first()

    # 2. Logic kiểm tra
    if not user:
        # Không tìm thấy thẻ
        return AccessCheckResponse(
            status="error",
            is_granted=False, # Không cho mở cổng
            message="Thẻ chưa được đăng ký trong hệ thống!"
        )
    
    if not user.is_active:
        # Thẻ bị khóa
        return AccessCheckResponse(
            status="error",
            is_granted=False, # Không cho mở cổng
            message="Tài khoản sinh viên đã bị khóa!",
            user_name=user.full_name
        )

    # 3. Hợp lệ -> Ra lệnh mở cổng
    return AccessCheckResponse(
        status="success",
        is_granted=True, # Lệnh MỞ CỔNG
        message="Xác thực thành công. Xin mời qua cổng!",
        user_name=user.full_name
    )

# API: Đăng nhập sinh viên để lấy JWT Token
@router.post("/login", response_model=Token, tags=["Authentication"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    # Sử dụng student_id làm username trong OAuth2
    statement = select(User).where(User.student_id == form_data.username)
    user = session.exec(statement).first()
    
    # Ở phiên bản Lab 04 này tạm thời chưa băm mật khẩu, có thể dùng card_uid làm password hoặc bỏ qua
    # Thực tế nên dùng passlib để verify password
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Tạo token payload
    expire = datetime.utcnow() + timedelta(minutes=60) # Token sống 60 phút
    to_encode = {"sub": user.student_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}