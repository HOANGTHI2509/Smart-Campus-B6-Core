import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Khởi tạo Engine dành riêng cho PostgreSQL hoặc SQLite dự phòng
db_url = settings.DATABASE_URL
if not db_url:
    # Fallback to local SQLite db inside the workspace
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "smart_campus.db")
    db_url = f"sqlite:///{db_path}"

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(db_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EnvironmentLog(Base):
    __tablename__ = "environment_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    device_id = Column(String, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    co2 = Column(Float, nullable=True)
    smoke = Column(Float, nullable=True)
    status = Column(String, nullable=True)
    raw_payload = Column(String, nullable=True) # JSON raw payload

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

