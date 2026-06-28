from sqlalchemy import Column, Integer, String, JSON
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(String, index=True)
    level = Column(String, index=True)
    source = Column(String, index=True)
    message = Column(String)
    payload = Column(JSON, nullable=True)
    status_code = Column(Integer)
