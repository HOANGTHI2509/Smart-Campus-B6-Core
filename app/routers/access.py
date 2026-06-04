from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models.core_models import User
from app.schemas.access_schemas import AccessCheckRequest, AccessCheckResponse
from app.core.dependencies import get_session

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