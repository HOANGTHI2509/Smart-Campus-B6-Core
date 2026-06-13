import sys
import os

# 2 Dòng thần thánh này ép Python phải lấy thư mục gốc của dự án (DVKN)
# làm gốc để tìm code, bất chấp bạn đang đứng ở đâu trong Terminal.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlmodel import SQLModel, create_engine
# Lần này import chắc chắn sẽ không lỗi
from app.models import core_models 
from dotenv import load_dotenv

load_dotenv()

# Chuỗi kết nối tới MySQL lấy hoàn toàn từ biến môi trường
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("🚨 Chưa cấu hình DATABASE_URL trong file .env!")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    print("Bắt đầu tạo bảng trong MySQL...")
    SQLModel.metadata.create_all(engine)
    print("=========================================")
    print("TẠO BẢNG THÀNH CÔNG! HÃY VÀO PHPMYADMIN KIỂM TRA.")
    print("=========================================")

if __name__ == "__main__":
    create_db_and_tables()