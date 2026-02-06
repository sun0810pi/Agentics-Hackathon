"""
FastAPI Backend - AI Agentic Fintech
Main Application Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from contextlib import asynccontextmanager

from app.api import auth, jobs, dashboard, health

# ===================================
# LOGGING
# ===================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===================================
# LIFESPAN
# ===================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting AI Agentic Fintech API...")
    yield
    logger.info("🛑 Shutting down AI Agentic Fintech API...")

# ===================================
# APP
# ===================================
app = FastAPI(
    title="AI Agentic Fintech API",
    description="Production-grade API for AI-powered invoice reconciliation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ===================================
# CORS
# ===================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================================
# MIDDLEWARE
# ===================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"← {response.status_code} ({process_time:.2f}s)")
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ===================================
# EXCEPTION HANDLER
# ===================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url)
        }
    )

# ===================================
# ROUTERS
# ===================================
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

# ===================================
# ROOT
# ===================================
@app.get("/")
async def root():
    return {
        "message": "AI Agentic Fintech API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)