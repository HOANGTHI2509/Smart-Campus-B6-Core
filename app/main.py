from fastapi import FastAPI
from app.routers import users, access, webhooks

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Smart Campus API - Phân hệ B6",
    description=(
        "Core Business API xử lý nghiệp vụ trung tâm của hệ thống Smart Campus. "
        "Điều phối giữa IoT Ingestion (B1), AI Vision (B4), "
        "Access Gate (B3) và Notification (B7)."
    ),
    version="1.0.0"
)

# --- Gắn các API Router vào hệ thống chính ---

# Router quản lý Users (CRUD)
app.include_router(users.router)

# Router kiểm soát ra vào & xác thực (JWT Login)
app.include_router(access.router)

# Router nhận Webhook từ B1 (IoT Ingestion) và B4 (AI Vision)
app.include_router(webhooks.router)


# --- Health Check ---
@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Server B6 đang hoạt động bình thường!", "status": "ok"}