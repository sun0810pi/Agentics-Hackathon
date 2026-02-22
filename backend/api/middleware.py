"""
backend/api/middleware.py
==========================
4 middleware layers (áp dụng từ trong ra ngoài):
1. JWTAuthMiddleware      — validate Cognito JWT mọi request
2. XRayMiddleware         — tạo X-Ray segment mỗi request
3. RateLimitMiddleware    — per-user token bucket
4. SecurityHeadersMiddleware — security headers mọi response
"""

import time, uuid, logging, os
from typing import Optional, Callable
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from api.rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)

PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


# ── 1. JWT Auth ───────────────────────────────────────────
class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Validates AWS Cognito JWT.
    Checks: signature (RS256), issuer, audience, expiration.
    Injects user_id / user_email / user_role into request.state.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._jwks_cache: Optional[list] = None
        self._jwks_cached_at: float = 0
        self._jwks_ttl: float = 3600.0

    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        token = self._extract(request)
        if not token:
            return JSONResponse(status_code=401, content={"error": "UNAUTHORIZED", "message": "Missing Authorization header"})

        claims = await self._validate(token)
        if not claims:
            return JSONResponse(status_code=401, content={"error": "UNAUTHORIZED", "message": "Token validation failed"})

        request.state.user_id    = claims.get("sub", "unknown")
        request.state.user_email = claims.get("email", claims.get("cognito:username", "unknown"))
        request.state.user_role  = claims.get("custom:role", "viewer")
        return await call_next(request)

    def _extract(self, request: Request) -> Optional[str]:
        auth = request.headers.get("Authorization", "")
        return auth[7:] if auth.startswith("Bearer ") else None

    async def _validate(self, token: str) -> Optional[dict]:
        try:
            from jose import jwt as jose_jwt
            header = jose_jwt.get_unverified_header(token)
            keys   = await self._get_jwks()
            key    = next((k for k in keys if k.get("kid") == header.get("kid")), None)
            if not key:
                logger.warning("No matching JWK found")
                return None

            pool_id = os.getenv("COGNITO_USER_POOL_ID", "")
            region  = os.getenv("AWS_REGION", "us-east-1")
            client  = os.getenv("COGNITO_CLIENT_ID", "")

            # Validates: signature, issuer, audience, expiration
            return jose_jwt.decode(token, key, algorithms=["RS256"],
                                   audience=client,
                                   issuer=f"https://cognito-idp.{region}.amazonaws.com/{pool_id}")
        except Exception as e:
            logger.warning(f"JWT validation failed: {e}")
            return None

    async def _get_jwks(self) -> list:
        if self._jwks_cache and (time.time() - self._jwks_cached_at) < self._jwks_ttl:
            return self._jwks_cache
        import httpx
        pool_id = os.getenv("COGNITO_USER_POOL_ID", "")
        region  = os.getenv("AWS_REGION", "us-east-1")
        url     = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
        async with httpx.AsyncClient() as c:
            resp = await c.get(url, timeout=5.0)
            resp.raise_for_status()
            self._jwks_cache     = resp.json().get("keys", [])
            self._jwks_cached_at = time.time()
            return self._jwks_cache


# ── 2. X-Ray ─────────────────────────────────────────────
class XRayMiddleware(BaseHTTPMiddleware):
    """Tạo X-Ray segment cho mỗi request. Thêm trace_id vào response header."""

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.time()

        try:
            from aws_xray_sdk.core import xray_recorder
            with xray_recorder.in_segment(f"agentflow-{request.method}-{request.url.path}") as seg:
                seg.put_annotation("request_id", request_id)
                seg.put_annotation("http.method", request.method)
                response = await call_next(request)
                seg.put_annotation("http.status",  response.status_code)
                seg.put_annotation("duration_ms",  round((time.time()-start)*1000, 2))
                trace_id = seg.trace_id
        except Exception:
            response = await call_next(request)
            trace_id = f"demo-{request_id[:8]}"

        response.headers["X-Trace-Id"]   = trace_id
        response.headers["X-Request-Id"] = request_id
        return response


# ── 3. Rate Limit ─────────────────────────────────────────
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-user token bucket. 429 + Retry-After khi vượt limit."""

    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            return await call_next(request)

        allowed, info = await get_rate_limiter().check(user_id, request.url.path)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"error": "RATE_LIMIT_EXCEEDED", "message": "Too many requests.",
                         "retry_after_seconds": info["reset_in_seconds"]},
                headers={"X-RateLimit-Limit":     str(info["limit"]),
                         "X-RateLimit-Remaining": "0",
                         "X-RateLimit-Reset":     info["reset_at"],
                         "Retry-After":           str(int(info["reset_in_seconds"])+1)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"]     = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"]     = info["reset_at"]
        return response


# ── 4. Security Headers ───────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Thêm security headers vào mọi response."""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"]   = "nosniff"
        response.headers["X-Frame-Options"]           = "DENY"
        response.headers["X-XSS-Protection"]          = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"]           = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"]   = "default-src 'self'; connect-src 'self' https://*.amazonaws.com"
        response.headers.pop("server", None)
        return response
