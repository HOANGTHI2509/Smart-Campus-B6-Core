# =============================================================
# Dockerfile - Smart Campus B6 (FastAPI)
# Multi-stage build để giảm kích thước image cuối cùng
# =============================================================

# --- Stage 1: Builder ---
# Dùng image đầy đủ để cài đặt dependencies (có build tools)
FROM python:3.11-slim AS builder

WORKDIR /build

# Sao chép file requirements và cài đặt vào thư mục cục bộ
# --no-cache-dir: không lưu cache pip (giảm kích thước)
# --prefix=/install: cài vào /install để dễ copy sang stage sau
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Stage 2: Runtime ---
# Chỉ lấy những gì cần thiết để chạy ứng dụng
FROM python:3.11-slim AS runtime

# Đặt thông tin tác giả
LABEL maintainer="Nhom B6 - Smart Campus DNU"
LABEL version="1.0.0"
LABEL description="Core Business API - Smart Campus Phân hệ B6"

# Thiết lập biến môi trường cho Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Copy các packages đã cài từ builder stage
COPY --from=builder /install /usr/local

# Copy toàn bộ source code của ứng dụng
COPY . .

# Expose port mà FastAPI/Uvicorn sẽ lắng nghe
EXPOSE 8000

# Lệnh khởi động server
# --host 0.0.0.0: Cho phép kết nối từ bên ngoài container
# --port 8000: Cổng lắng nghe
# --workers 2: 2 worker processes để xử lý đồng thời
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
