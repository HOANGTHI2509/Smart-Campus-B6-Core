from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class AccessLogAnalyticsResponse(BaseModel):
    id: int
    timestamp: datetime
    access_date: date
    access_hour: int
    status: str
    reason: Optional[str] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    student_id: Optional[str] = None
    user_type: Optional[str] = None
    device_id: Optional[int] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
