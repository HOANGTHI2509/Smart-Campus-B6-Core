from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    API_PORT: int = 8000
    
    # ----------------------------------------------------
    # KIẾN TRÚC IP TẬP TRUNG (Theo chuẩn Radmin VPN của lớp)
    # ----------------------------------------------------
    B4_AI_VISION_URL: str = "http://26.x.x.x:4010"
    B3_ACCESS_GATE_URL: str = "http://26.x.x.x:8000"
    B7_NOTIFICATION_URL: str = "http://26.x.x.x:8000"
    B5_ANALYTICS_URL: str = "http://26.x.x.x:8000"
    
    # ----------------------------------------------------
    # THÔNG TIN BẢO MẬT (Các giá trị này rỗng, bắt buộc đọc từ .env)
    # ----------------------------------------------------
    MQTT_BROKER_URL: str = ""
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    DATABASE_URL: str = ""

    class Config:
        env_file = ".env"

# Khởi tạo một object setting chung để các file khác import dùng
settings = Settings()
