from pydantic import BaseModel

# Khung dữ liệu yêu cầu Client (Web/App) gửi lên khi tạo User mới
# Chú ý: Không có trường 'id' vì id do DB tự tạo
class UserCreate(BaseModel):
    full_name: str
    student_id: str
    card_uid: str

# Khung dữ liệu B6 sẽ trả về cho Client
class UserResponse(BaseModel):
    id: int
    full_name: str
    student_id: str
    card_uid: str
    role: str
    is_active: bool