"""
backend/api/middleware.py
==========================
4 middleware layers (áp dụng từ trong ra ngoài):
1. JWTAuthMiddleware      — validate Cognito JWT mọi request
2. XRayMiddleware         — tạo X-Ray segment mỗi request
3. RateLimitMiddleware    — per-user token bucket
4. SecurityHeadersMiddleware — security headers mọi response

DEMO MODE:
  - Set env DEMO_MODE=true  →  tất cả requests bypass JWT
  - Hoặc gửi header X-Demo-Mode: true  →  bypass JWT cho request đó
  - Hoặc /api/analyze với mode=demo trong body → bypass JWT
  → Dùng khi chạy local / hackathon demo mà chưa setup Cognito
"""

import time, uuid, logging, os, asyncio
from typing import Optional, Callable
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from api.rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)

# Paths không cần auth bao giờ
PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}

# Demo user inject vào request.state khi bypass JWT
DEMO_USER = {"user_id": "demo-user-001", "user_email": "demo@agentflow.ai", "user_role": "admin"}


def _is_demo_mode() -> bool:
    """True nếu DEMO_MODE=true trong env."""
    return os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")


# ── 1. JWT Auth ───────────────────────────────────────────
class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Validates AWS Cognito JWT.
    Checks: signature (RS256), issuer, audience, expiration.
    Injects user_id / user_email / user_role into request.state.

    Bypass JWT (DEMO MODE):
      - DEMO_MODE=true env var
      - Header: X-Demo-Mode: true
      - Body field mode=demo (detected via URL path only for analyze endpoint)
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._jwks_cache: Optional[list] = None
        self._jwks_cached_at: float = 0
        self._jwks_ttl: float = 3600.0
        self._jwks_lock = asyncio.Lock()  # prevent concurrent JWKS fetches

    async def dispatch(self, request: Request, call_next: Callable):
        # 1. Always allow public paths
        if request.url.path in PUBLIC_PATHS:
            self._inject_state(request, DEMO_USER)
            return await call_next(request)

        # 2. Global demo mode (env var) or per-request demo header
        if _is_demo_mode() or request.headers.get("X-Demo-Mode", "").lower() == "true":
            logger.debug(f"Demo mode bypass: {request.url.path}")
            self._inject_state(request, DEMO_USER)
            return await call_next(request)

        # 3. Real JWT validation
        token = self._extract(request)
        if not token:
            return JSONResponse(
                status_code=401,
                content={"error": "UNAUTHORIZED", "message": "Missing Authorization header. "
                         "Set DEMO_MODE=true or send X-Demo-Mode: true for local testing."},
            )

        claims = await self._validate(token)
        if not claims:
            return JSONResponse(
                status_code=401,
                content={"error": "UNAUTHORIZED", "message": "Token validation failed"},
            )

        self._inject_state(request, {
            "user_id":    claims.get("sub", "unknown"),
            "user_email": claims.get("email", claims.get("cognito:username", "unknown")),
            "user_role":  claims.get("custom:role", "viewer"),
        })
        return await call_next(request)

    def _inject_state(self, request: Request, user: dict) -> None:
        request.state.user_id    = user["user_id"]
        request.state.user_email = user["user_email"]
        request.state.user_role  = user["user_role"]

    def _extract(self, request: Request) -> Optional[str]:
        auth = request.headers.get("Authorization", "")
        return auth[7:] if auth.startswith("Bearer ") else None

    async def _validate(self, token: str) -> Optional[dict]:
        try:
            from jose import jwt as jose_jwt, JWTError
            header = jose_jwt.get_unverified_header(token)
            keys   = await self._get_jwks()
            key    = next((k for k in keys if k.get("kid") == header.get("kid")), None)
            if not key:
                logger.warning("JWT: no matching kid in JWKS")
                return None

            pool_id = os.getenv("COGNITO_USER_POOL_ID", "")
            region  = os.getenv("AWS_REGION", "us-east-1")
            client  = os.getenv("COGNITO_CLIENT_ID", "")

            if not pool_id or not client:
                logger.error("JWT: COGNITO_USER_POOL_ID or COGNITO_CLIENT_ID not set")
                return None

            # Validates: signature (RS256), issuer, audience, expiration
            return jose_jwt.decode(
                token, key, algorithms=["RS256"],
                audience=client,
                issuer=f"https://cognito-idp.{region}.amazonaws.com/{pool_id}",
            )
        except Exception as e:
            logger.warning(f"JWT validation failed: {type(e).__name__}: {e}")
            return None

    async def _get_jwks(self) -> list:
        """Fetch JWKS with 1-hour cache and lock to prevent stampede."""
        if self._jwks_cache and (time.time() - self._jwks_cached_at) < self._jwks_ttl:
            return self._jwks_cache

        async with self._jwks_lock:
            # Double-check after acquiring lock
            if self._jwks_cache and (time.time() - self._jwks_cached_at) < self._jwks_ttl:
                return self._jwks_cache

            pool_id = os.getenv("COGNITO_USER_POOL_ID", "")
            region  = os.getenv("AWS_REGION", "us-east-1")
            url     = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
            try:
                import httpx
                async with httpx.AsyncClient(timeout=5.0) as c:
                    resp = await c.get(url)
                    resp.raise_for_status()
                    self._jwks_cache     = resp.json().get("keys", [])
                    self._jwks_cached_at = time.time()
                    logger.info(f"JWKS refreshed: {len(self._jwks_cache)} keys")
            except Exception as e:
                logger.error(f"JWKS fetch failed: {e}")
                if not self._jwks_cache:
                    self._jwks_cache = []
            return self._jwks_cache


# ── 2. X-Ray ─────────────────────────────────────────────
class XRayMiddleware(BaseHTTPMiddleware):
    """
    Tạo X-Ray segment mỗi request.
    Graceful fallback khi X-Ray không available (local dev / demo).

    Fix: call_next được gọi ĐÚNG MỘT LẦN bất kể X-Ray có hay không.
    Pattern: check availability first, then branch — không nested try/except.
    """

    _xray_available: Optional[bool] = None   # cached after first check

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.time()

        # Check X-Ray availability once, cache result
        if self._xray_available is None:
            try:
                from aws_xray_sdk.core import xray_recorder as _xr
                _xr.configure(context_missing="LOG_ERROR")
                XRayMiddleware._xray_available = True
            except Exception:
                XRayMiddleware._xray_available = False

        trace_id = f"1-{hex(int(time.time()))[2:]}-{request_id.replace('-','')[:24]}"

        if self._xray_available:
            trace_id = await self._dispatch_with_xray(request, call_next, request_id, start, trace_id)
            # _dispatch_with_xray returns the response via request.state hack — see below
            response = request.state._xray_response
        else:
            # No X-Ray — just call next once, cleanly
            response = await call_next(request)

        response.headers["X-Trace-Id"]   = trace_id
        response.headers["X-Request-Id"] = request_id
        return response

    async def _dispatch_with_xray(
        self, request: Request, call_next: Callable,
        request_id: str, start: float, fallback_trace_id: str,
    ) -> str:
        """Returns trace_id. Stores response in request.state._xray_response."""
        try:
            from aws_xray_sdk.core import xray_recorder
            seg_name = f"agentflow {request.method} {request.url.path}"
            with xray_recorder.in_segment(seg_name) as seg:
                seg.put_annotation("request_id",  request_id)
                seg.put_annotation("http_method",  request.method)
                response = await call_next(request)   # called exactly ONCE here
                seg.put_annotation("http_status",  response.status_code)
                seg.put_annotation("duration_ms",  round((time.time()-start)*1000, 2))
                request.state._xray_response = response
                return getattr(seg, "trace_id", fallback_trace_id)
        except Exception as e:
            logger.warning(f"X-Ray segment failed: {e}")
            # X-Ray failed mid-request — response may already exist
            if not hasattr(request.state, "_xray_response"):
                request.state._xray_response = await call_next(request)
            return fallback_trace_id


# ── 3. Rate Limit ─────────────────────────────────────────
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-user token bucket. 429 + Retry-After khi vượt limit."""

    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            # JWT middleware chưa chạy hoặc bypass — cho qua
            return await call_next(request)

        allowed, info = await get_rate_limiter().check(user_id, request.url.path)

        if not allowed:
            retry_after = int(info.get("reset_in_seconds", 10)) + 1
            return JSONResponse(
                status_code=429,
                content={
                    "error":   "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many requests. Retry in {retry_after}s.",
                    "retry_after_seconds": info.get("reset_in_seconds", 10),
                    "limit":   info.get("limit", 15),
                },
                headers={
                    "X-RateLimit-Limit":     str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset":     info["reset_at"],
                    "Retry-After":           str(retry_after),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"]     = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"]     = info["reset_at"]
        return response


# ── 4. Security Headers ───────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Thêm security headers vào mọi response. Remove server fingerprint."""

    # Pre-compute header dict — không tạo lại mỗi request
    _HEADERS = {
        "X-Content-Type-Options":   "nosniff",
        "X-Frame-Options":           "DENY",
        "X-XSS-Protection":          "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Referrer-Policy":           "strict-origin-when-cross-origin",
        "Permissions-Policy":        "geolocation=(), microphone=(), camera=()",
        "Content-Security-Policy":   (
            "default-src 'self'; "
            "connect-src 'self' https://*.amazonaws.com https://cognito-idp.*.amazonaws.com; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'"
        ),
    }

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        for k, v in self._HEADERS.items():
            response.headers[k] = v
        # Remove server fingerprint
        response.headers.pop("server", None)
        response.headers.pop("x-powered-by", None)
        return response
