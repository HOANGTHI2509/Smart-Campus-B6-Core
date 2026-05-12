from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.models.core_models import User
from app.schemas.user_schemas import UserCreate, UserResponse
from app.core.database import engine

# Tạo router quản lý User
router = APIRouter(prefix="/api/v1/users", tags=["Users"])

# Dependency để mở phiên làm việc (Session) với Database
def get_session():
    with Session(engine) as session:
        yield session

# API 1: Thêm sinh viên mới
@router.post("/", response_model=UserResponse)
def create_user(user_in: UserCreate, session: Session = Depends(get_session)):
    # 1. Kiểm tra xem mã sinh viên hoặc thẻ đã tồn tại chưa
    statement = select(User).where(
        (User.student_id == user_in.student_id) | (User.card_uid == user_in.card_uid)
    )
    existing_user = session.exec(statement).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Mã sinh viên hoặc Mã thẻ đã tồn tại!")
    
    # 2. Tạo User mới và lưu vào DB
    db_user = User(
        full_name=user_in.full_name,
        student_id=user_in.student_id,
        card_uid=user_in.card_uid
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user) # Lấy lại dữ liệu từ DB (để có được ID vừa tạo)
    
    return db_user

# API 2: Lấy thông tin sinh viên theo ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên này!")
    return user