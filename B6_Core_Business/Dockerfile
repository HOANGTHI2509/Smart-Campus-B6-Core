FROM python:3.11-slim

WORKDIR /app

# Copy requirements trước để tận dụng cache của Docker
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào image
COPY . .

# Expose port 8000 ra ngoài (Đúng theo yêu cầu thầy)
EXPOSE 8000

# Khởi chạy Uvicorn, ràng buộc vào địa chỉ 0.0.0.0 để nhận request từ máy khác
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
