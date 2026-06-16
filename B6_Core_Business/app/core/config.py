from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    API_PORT: int = 8000
    
    # ----------------------------------------------------
    # KIẾN TRÚC IP TẬP TRUNG (Dành cho Demo)
    # ----------------------------------------------------
    LAN_HOST_IP: str = "127.0.0.1"  # Sẽ bị ghi đè bởi file .env
    B4_NGROK_URL: str = ""          # Sẽ bị ghi đè bởi file .env
    B7_NGROK_URL: str = ""          # Sẽ bị ghi đè bởi file .env
    B3_NGROK_URL: str = ""          # Sẽ bị ghi đè bởi file .env

    @property
    def B4_AI_VISION_URL(self) -> str:
        return self.B4_NGROK_URL if self.B4_NGROK_URL else f"http://{self.LAN_HOST_IP}:4010"

    @property
    def B3_ACCESS_GATE_URL(self) -> str:
        return self.B3_NGROK_URL if self.B3_NGROK_URL else f"http://{self.LAN_HOST_IP}:8080"
        
    @property
    def B7_NOTIFICATION_URL(self) -> str:
        return self.B7_NGROK_URL if self.B7_NGROK_URL else f"http://{self.LAN_HOST_IP}:5000"
        
    @property
    def B5_ANALYTICS_URL(self) -> str:
        return f"http://{self.LAN_HOST_IP}:9000"
    
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
