"""
backend/main.py
================
FastAPI app factory. Registers middleware và routes.
Middleware order (bottom-up = first executed first):
  JWTAuth → XRay → RateLimit → SecurityHeaders
"""

import logging, os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.middleware import JWTAuthMiddleware, XRayMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware
from services.xray_tracer import init_xray
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_xray("agentflow-backend")
    try:
        from services.database import init_db_pool, init_schema
        await init_db_pool(); await init_schema()
        logger.info("Database ready")
    except Exception as e:
        logger.warning(f"DB unavailable (demo mode): {e}")
    logger.info(f"AgentFlow Backend v{config.APP_VERSION} started")
    yield
    try:
        from services.database import close_db_pool
        await close_db_pool()
    except: pass


def create_app() -> FastAPI:
    app = FastAPI(title="AgentFlow Finance Guard API", version=config.APP_VERSION,
                  description="17-Agent AI-Powered Fraud Detection", lifespan=lifespan)

    origins = config.ALLOWED_ORIGINS.split(",")
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                       allow_methods=["GET","POST"], allow_headers=["Authorization","Content-Type","X-Request-Id"],
                       expose_headers=["X-Trace-Id","X-Request-Id","X-RateLimit-Limit","X-RateLimit-Remaining"])

    # Middleware applied bottom → top (SecurityHeaders outermost)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(XRayMiddleware)
    app.add_middleware(JWTAuthMiddleware)

    app.include_router(router)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
