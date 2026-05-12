from sqlmodel import SQLModel, Field
from typing import Optional

# Định nghĩa bảng Users
class User(SQLModel, table=True):
    __tablename__ = "users" # Đặt tên bảng tường minh
    
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    student_id: str = Field(unique=True, index=True)
    card_uid: str = Field(unique=True, index=True)
    role: str = Field(default="student")
    is_active: bool = Field(default=True)

# Định nghĩa bảng Devices (Thiết bị)
class Device(SQLModel, table=True):
    __tablename__ = "devices"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    device_name: str
    device_type: str # gate, sensor, camera
    ip_address: Optional[str] = None
    status: str = Field(default="online")