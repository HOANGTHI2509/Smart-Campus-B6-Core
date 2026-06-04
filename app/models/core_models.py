from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, time

# -----------------
# 1. Bảng Devices (Thiết bị)
# -----------------
class Device(SQLModel, table=True):
    __tablename__ = "devices"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    device_name: str
    device_type: str # gate, sensor, camera
    ip_address: Optional[str] = None
    status: str = Field(default="online")
    
    # Quan hệ 1-N với AccessLog
    access_logs: List["AccessLog"] = Relationship(back_populates="device")

# -----------------
# 2. Bảng Users (Sinh viên/Giảng viên)
# -----------------
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    student_id: str = Field(unique=True, index=True)
    card_uid: str = Field(unique=True, index=True)
    role: str = Field(default="student")
    is_active: bool = Field(default=True)
    
    # Quan hệ 1-N
    schedules: List["Schedule"] = Relationship(back_populates="user")
    access_logs: List["AccessLog"] = Relationship(back_populates="user")

# -----------------
# 3. Bảng Schedule (Thời khóa biểu)
# -----------------
class Schedule(SQLModel, table=True):
    __tablename__ = "schedules"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    room_id: str
    start_time: time
    end_time: time
    day_of_week: int # 2: Thứ 2, 3: Thứ 3..., 8: Chủ nhật
    
    # Quan hệ ngược lại
    user: Optional[User] = Relationship(back_populates="schedules")

# -----------------
# 4. Bảng AccessLog (Lịch sử ra vào)
# -----------------
class AccessLog(SQLModel, table=True):
    __tablename__ = "access_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    device_id: Optional[int] = Field(default=None, foreign_key="devices.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str # "success", "failed"
    reason: Optional[str] = None # Lý do thất bại (sai thẻ, không có lịch,...)
    
    # Quan hệ ngược lại
    user: Optional[User] = Relationship(back_populates="access_logs")
    device: Optional[Device] = Relationship(back_populates="access_logs")