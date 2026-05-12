from pydantic import BaseModel
from typing import Optional

# Dữ liệu nhóm B3 (Cổng) sẽ gửi lên cho B6
class AccessCheckRequest(BaseModel):
    card_uid: str
    gate_id: str

# Dữ liệu B6 sẽ trả về cho B3 để ra lệnh mở/đóng cổng
class AccessCheckResponse(BaseModel):
    status: str
    is_granted: bool
    message: str
    user_name: Optional[str] = None