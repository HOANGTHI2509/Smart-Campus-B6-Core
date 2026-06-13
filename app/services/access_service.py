from sqlmodel import Session, select
from datetime import datetime, time
from typing import Optional, Tuple
from app.models.core_models import User, Schedule, Role, AccessLog, Device

class AccessService:
    def __init__(self, session: Session):
        self.session = session

    def verify_access(self, card_uid: str, device_id: int) -> Tuple[bool, str, Optional[User]]:
        """
        Kiểm tra tính hợp lệ khi người dùng quẹt thẻ.
        Trả về: (is_allowed, reason, User)
        """
        # 1. Tìm User theo card_uid
        statement = select(User).where(User.card_uid == card_uid)
        user = self.session.exec(statement).first()

        if not user:
            self._log_access(None, device_id, "failed", "Thẻ không tồn tại trong hệ thống")
            return False, "User not found", None

        # 2. Kiểm tra thẻ có bị khóa không
        if not user.is_active:
            self._log_access(user.id, device_id, "failed", "Thẻ đã bị khóa")
            return False, "Card is locked", user

        # 3. Lấy thông tin Role
        role = user.role
        if not role:
            # Fallback nếu mất dữ liệu role
            role_name = "student"
        else:
            role_name = role.role_name

        # 4. Đặc quyền của Admin và Giảng viên (Luôn cho phép qua)
        if role_name in ["admin", "lecturer"]:
            self._log_access(user.id, device_id, "success", f"Đặc quyền {role_name}")
            return True, "Access granted (Privileged)", user

        # 5. Logic đối với Sinh viên (Cần đối chiếu Thời khóa biểu)
        now = datetime.now()
        current_time = now.time()
        # Trong Python, isoweekday() trả về Thứ 2 = 1, Thứ 3 = 2... Chủ nhật = 7
        # Trong database có thể ta quy ước Thứ 2 = 2, Thứ 3 = 3... Chủ nhật = 8
        current_day = now.isoweekday() + 1 

        # Truy vấn lịch học của sinh viên trong ngày hôm nay
        schedule_stmt = select(Schedule).where(
            Schedule.user_id == user.id,
            Schedule.day_of_week == current_day
        )
        schedules = self.session.exec(schedule_stmt).all()

        if not schedules:
            self._log_access(user.id, device_id, "failed", "Không có lịch học hôm nay")
            return False, "No schedule today", user

        # Kiểm tra xem có nằm trong khung giờ học không (Cho phép đi trễ hoặc đến sớm 30 phút)
        # Để đơn giản, ta tính bằng phút từ 00:00
        current_minutes = current_time.hour * 60 + current_time.minute
        
        for sched in schedules:
            start_minutes = sched.start_time.hour * 60 + sched.start_time.minute
            end_minutes = sched.end_time.hour * 60 + sched.end_time.minute
            
            # Cho phép đến sớm 30 phút và ở lại trễ 30 phút
            if (start_minutes - 30) <= current_minutes <= (end_minutes + 30):
                self._log_access(user.id, device_id, "success", f"Hợp lệ (Phòng {sched.room_id})")
                return True, "Access granted", user

        self._log_access(user.id, device_id, "failed", "Sai khung giờ học")
        return False, "Outside of schedule hours", user

    def _log_access(self, user_id: Optional[int], device_id: int, status: str, reason: str):
        """Ghi log ra vào vào Database"""
        log = AccessLog(
            user_id=user_id,
            device_id=device_id,
            status=status,
            reason=reason,
            timestamp=datetime.utcnow()
        )
        self.session.add(log)
        self.session.commit()
