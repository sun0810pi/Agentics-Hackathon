"""
backend/main.py
================
FastAPI application factory.
- Registers all middleware (order matters!)
- Includes all routers
- Handles startup/shutdown events
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.middleware import (
    JWTAuthMiddleware,
    XRayMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from services.xray_tracer import init_xray

# ── Logging ───────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Startup / Shutdown ────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, clean up on shutdown."""
    # Init X-Ray
    init_xray("agentflow-backend")

    # Init DB pool (will fail gracefully if DB not configured)
    try:
        from services.database import init_db_pool, init_schema
        await init_db_pool()
        await init_schema()
        logger.info("Database ready")
    except Exception as e:
        logger.warning(f"DB init failed (demo mode will be used): {e}")

    logger.info("AgentFlow Backend v3.1.0 started")
    yield

    # Cleanup
    try:
        from services.database import close_db_pool
        await close_db_pool()
    except Exception:
        pass
    logger.info("AgentFlow Backend shutdown")


# ── App factory ───────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="AgentFlow Finance Guard API",
        description="17-Agent AI-Powered Fraud Detection Backend",
        version="3.1.0",
        docs_url="/docs",       # Swagger UI
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "https://yourapp.streamlit.app,http://localhost:8501"
    ).split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-Request-Id"],
        expose_headers=["X-Trace-Id", "X-Request-Id",
                        "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    )

    # ── Middleware stack (applied bottom-up) ─────────
    # 4. Security headers (outermost — wraps everything)
    app.add_middleware(SecurityHeadersMiddleware)
    # 3. Rate limiting
    app.add_middleware(RateLimitMiddleware)
    # 2. X-Ray tracing
    app.add_middleware(XRayMiddleware)
    # 1. JWT auth (innermost — runs first)
    app.add_middleware(JWTAuthMiddleware)

    # ── Routes ───────────────────────────────────────
    app.include_router(router)

    return app


app = create_app()


# ── Local dev entry point ────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
