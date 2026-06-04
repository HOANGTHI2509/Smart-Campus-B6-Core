from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from jose import JWTError, jwt
import os

from app.core.database import engine
from app.models.core_models import User

# Cấu hình JWT (Trong thực tế nên để trong file .env)
SECRET_KEY = os.getenv("SECRET_KEY", "smart-campus-b6-secret-key-lab04")
ALGORITHM = "HS256"

# Cấu hình URL endpoint để lấy token (Login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access/login")

def get_session():
    """Dependency cung cấp Database session cho mỗi request"""
    with Session(engine) as session:
        yield session

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    """
    Dependency dùng để bảo vệ các API private.
    Xác thực JWT Token và trả về object User hiện tại.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập (Token không hợp lệ)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Giải mã token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id: str = payload.get("sub")
        if student_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Lấy thông tin User từ Database
    statement = select(User).where(User.student_id == student_id)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản người dùng đã bị khóa")
        
    return user
