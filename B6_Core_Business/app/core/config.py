from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    API_PORT: int = 8000
    
    # Partner URLs (Mạng LAN)
    B4_AI_VISION_URL: str = "http://172.20.10.5:4010"
    B3_ACCESS_GATE_URL: str = "http://172.20.10.6:8080"
    B7_NOTIFICATION_URL: str = "http://172.20.10.7:5000"
    B5_ANALYTICS_URL: str = "http://172.20.10.8:9000"
    
    # MQTT Config
    MQTT_BROKER_URL: str = "f6f78e87db4a4c189dd3d706745a5e93.s1.eu.hivemq.cloud"
    MQTT_PORT: int = 8883
    MQTT_USERNAME: str = "DVKN_IOT_2026"
    MQTT_PASSWORD: str = "ThaiBao12A@"

    class Config:
        env_file = ".env"

# Khởi tạo một object setting chung để các file khác import dùng
settings = Settings()
