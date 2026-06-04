import json
from fastapi.openapi.utils import get_openapi
from app.main import app

# Trích xuất OpenAPI Schema từ FastAPI
openapi_schema = get_openapi(
    title=app.title,
    version=app.version,
    openapi_version=app.openapi_version,
    description=app.description,
    routes=app.routes,
)

# Lưu thành file json
with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

print("Đã xuất file OpenAPI thành công ra file openapi.json!")
