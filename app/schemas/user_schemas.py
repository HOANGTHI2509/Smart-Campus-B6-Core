from pydantic import BaseModel, Field
from typing import Optional

# Khung dữ liệu yêu cầu Client (Web/App) gửi lên khi tạo User mới
# Chú ý: Không có trường 'id' vì id do DB tự tạo
class UserCreate(BaseModel):
    full_name: str
    student_id: str
    card_uid: str
    password: str = Field(
        ...,
        min_length=6,
        description="Mật khẩu tối thiểu 6 ký tự. Sẽ được mã hóa bcrypt trước khi lưu."
    )

# Khung dữ liệu B6 sẽ trả về cho Client (không bao giờ trả về password)
class UserResponse(BaseModel):
    id: int
    full_name: str
    student_id: str
    card_uid: str
    is_active: bool