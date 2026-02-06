# FILE: app/main.py
from fastapi import FastAPI
from app.api import routes  # <-- Import file routes mình vừa tạo

app = FastAPI(
    title="Fintech Agent Control Plane",
    version="2.0.0",
    description="Hệ thống backend điều phối các Agent kiểm toán"
)

# Gắn router vào (prefix giúp đường dẫn đẹp hơn: /api/v1/process-batch)
app.include_router(routes.router, prefix="/api/v1", tags=["Audit Transactions"])

@app.get("/")
def healthcheck():
    return {"status": "System Operational", "service": "Control Plane"}
