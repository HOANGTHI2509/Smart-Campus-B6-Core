from fastapi import FastAPI
from app.routers import users, access, analytics

# Khoi tao ung dung FastAPI
app = FastAPI(
    title="Smart Campus API - Phan he B6",
    description="Core Business API xu ly nghiep vu trung tam",
    version="1.0.0"
)

# Gan cac API Router vao he thong chinh
app.include_router(users.router)
app.include_router(access.router)
app.include_router(analytics.router)

# Nut test he thong
@app.get("/")
def read_root():
    return {"message": "Server B6 dang hoat dong binh thuong!"}
