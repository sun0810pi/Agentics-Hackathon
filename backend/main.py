"""
backend/main.py
================
FastAPI app factory.

Middleware stack (bottom → top = inner → outer, outer executes first):
  Layer 4 (outermost): SecurityHeaders — always last to touch response
  Layer 3:             RateLimit       — needs user_id from JWT
  Layer 2:             XRay            — wraps full request for tracing
  Layer 1 (innermost): JWT             — runs first, injects user_id

Demo mode:
  Set DEMO_MODE=true → JWT bypass, DB optional, no AWS required
  uvicorn main:app --reload (auto demo mode in dev)
"""

import logging, os, sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.middleware import (
    JWTAuthMiddleware, XRayMiddleware,
    RateLimitMiddleware, SecurityHeadersMiddleware,
)
from services.xray_tracer import init_xray
import config

logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def _validate_startup_config() -> None:
    """Warn loudly if production env vars are missing."""
    is_demo = os.getenv("DEMO_MODE", "false").lower() in ("true","1","yes")
    if is_demo:
        logger.info("🟡 DEMO MODE — JWT, DB, and AWS calls are simulated")
        return

    required = {
        "COGNITO_USER_POOL_ID": os.getenv("COGNITO_USER_POOL_ID",""),
        "COGNITO_CLIENT_ID":    os.getenv("COGNITO_CLIENT_ID",""),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        logger.error(
            f"⛔ Missing env vars: {missing}. "
            "Set DEMO_MODE=true for local dev, or provide all Cognito vars for production."
        )
        # Don't crash — allow startup so /health still works


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown logic."""
    logger.info(f"🚀 AgentFlow Backend v{config.APP_VERSION} starting...")

    _validate_startup_config()
    init_xray("agentflow-backend")

    # Database — graceful fallback to demo metrics if unavailable
    try:
        from services.database import init_db_pool, init_schema
        await init_db_pool()
        await init_schema()
        logger.info("✅ Database connected and schema ready")
    except Exception as e:
        logger.warning(f"⚠️  Database unavailable ({e}) — running in demo mode")

    # Pre-warm orchestrator (avoids cold-start latency on first /api/analyze)
    try:
        from agents.orchestrator import AgentOrchestrator
        _ = AgentOrchestrator()
        logger.info("✅ Agent orchestrator pre-warmed")
    except Exception as e:
        logger.warning(f"⚠️  Orchestrator pre-warm failed: {e}")

    logger.info("✅ All systems ready. Accepting requests.")
    yield

    # Graceful shutdown
    try:
        from services.database import close_db_pool
        await close_db_pool()
        logger.info("DB pool closed")
    except Exception:
        pass
    logger.info("AgentFlow Backend shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgentFlow Finance Guard API",
        version=config.APP_VERSION,
        description=(
            "17-Agent AI-Powered Invoice Fraud Detection. "
            "Set DEMO_MODE=true for local testing without AWS."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS — only allow configured origins
    origins = [o.strip() for o in config.ALLOWED_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-Id", "X-Demo-Mode"],
        expose_headers=["X-Trace-Id", "X-Request-Id", "X-RateLimit-Limit",
                        "X-RateLimit-Remaining", "X-RateLimit-Reset"],
        max_age=3600,   # cache preflight 1hr
    )

    # Middleware stack — add_middleware is LIFO (last added = outermost = runs first)
    app.add_middleware(SecurityHeadersMiddleware)   # 4: outermost — last to see response
    app.add_middleware(RateLimitMiddleware)          # 3: needs user_id from JWT
    app.add_middleware(XRayMiddleware)              # 2: wraps whole request
    app.add_middleware(JWTAuthMiddleware)           # 1: runs first, injects user_id

    app.include_router(router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    # Auto-enable demo mode in local dev
    if not os.getenv("DEMO_MODE"):
        os.environ["DEMO_MODE"] = "true"
        logger.info("Auto-enabled DEMO_MODE for local dev")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
