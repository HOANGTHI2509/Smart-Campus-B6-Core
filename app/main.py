from fastapi import FastAPI
from app.routers import users
from app.routers import users, access

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Smart Campus API - Phân hệ B6",
    description="Core Business API xử lý nghiệp vụ trung tâm",
    version="1.0.0"
)

# Gắn các API Router vào hệ thống chính
app.include_router(users.router)
app.include_router(access.router)

# Nút test hệ thống
@app.get("/")
def read_root():
    return {"message": "Server B6 đang hoạt động bình thường!"}