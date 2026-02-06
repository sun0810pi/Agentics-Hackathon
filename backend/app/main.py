from fastapi import FastAPI
from app.api.jobs import router as jobs_router

app = FastAPI(
    title="Fintech Invoice Control Plane",
    version="1.0.0"
)

app.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])

@app.get("/")
def healthcheck():
    return {"status": "ok"}
