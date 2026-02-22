"""
backend/api/middleware.py
==========================
FastAPI middleware stack:
1. JWTAuthMiddleware  — validates Cognito JWT on every protected request
2. XRayMiddleware     — creates X-Ray segment per request
3. RateLimitMiddleware— enforces per-user token bucket limits
4. SecurityHeadersMiddleware — adds security headers to every response
"""

import time
import uuid
import json
import logging
import os
from typing import Optional, Callable

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from api.rate_limiter import get_rate_limiter
from services.xray_tracer import get_trace_id, add_annotation

logger = logging.getLogger(__name__)

# ── Endpoints that don't need JWT auth ───────────────
PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


# =====================================================
# 1. JWT AUTH MIDDLEWARE
# =====================================================

class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Validates AWS Cognito JWT tokens.
    Injects user_id and user_email into request.state for downstream use.

    Token validation steps:
    1. Extract Bearer token from Authorization header
    2. Decode JWT header to get `kid` (key ID)
    3. Fetch Cognito JWKS (cached)
    4. Verify signature, expiry, issuer, audience
    5. Reject if any check fails
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._jwks_cache: Optional[dict] = None
        self._jwks_cached_at: float = 0
        self._jwks_ttl = 3600  # refresh JWKS hourly

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip auth for public paths
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        token = self._extract_token(request)
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "UNAUTHORIZED", "message": "Missing or invalid Authorization header"},
            )

        claims = await self._validate_token(token)
        if not claims:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "UNAUTHORIZED", "message": "Token validation failed"},
            )

        # Inject into request state
        request.state.user_id    = claims.get("sub", "unknown")
        request.state.user_email = claims.get("email", claims.get("username", "unknown"))
        request.state.user_role  = claims.get("custom:role", "viewer")
        request.state.token_exp  = claims.get("exp", 0)

        return await call_next(request)

    def _extract_token(self, request: Request) -> Optional[str]:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:]
        return None

    async def _validate_token(self, token: str) -> Optional[dict]:
        """Validate JWT signature and claims against Cognito JWKS."""
        try:
            from jose import jwk, jwt as jose_jwt
            from jose.utils import base64url_decode
            import json as _json

            # Decode header without verification to get kid
            header = jose_jwt.get_unverified_header(token)
            kid = header.get("kid")

            # Get JWKS
            keys = await self._get_jwks()
            matching_key = next((k for k in keys if k.get("kid") == kid), None)
            if not matching_key:
                logger.warning(f"No matching JWK for kid={kid}")
                return None

            # Validate
            user_pool_id = os.getenv("COGNITO_USER_POOL_ID", "")
            region       = os.getenv("AWS_REGION", "us-east-1")
            client_id    = os.getenv("COGNITO_CLIENT_ID", "")
            issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"

            claims = jose_jwt.decode(
                token,
                matching_key,
                algorithms=["RS256"],
                audience=client_id,
                issuer=issuer,
            )
            return claims

        except Exception as e:
            logger.warning(f"JWT validation failed: {type(e).__name__}: {e}")
            return None

    async def _get_jwks(self) -> list:
        """Fetch JWKS from Cognito, with 1-hour cache."""
        now = time.time()
        if self._jwks_cache and (now - self._jwks_cached_at) < self._jwks_ttl:
            return self._jwks_cache

        import httpx
        user_pool_id = os.getenv("COGNITO_USER_POOL_ID", "")
        region       = os.getenv("AWS_REGION", "us-east-1")
        url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=5.0)
            resp.raise_for_status()
            data = resp.json()
            self._jwks_cache = data.get("keys", [])
            self._jwks_cached_at = now
            return self._jwks_cache


# =====================================================
# 2. X-RAY MIDDLEWARE
# =====================================================

class XRayMiddleware(BaseHTTPMiddleware):
    """
    Creates an X-Ray segment for every incoming request.
    Adds trace_id to response headers so frontend can display it.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            from aws_xray_sdk.core import xray_recorder
            with xray_recorder.in_segment(f"agentflow-{request.method}-{request.url.path}") as seg:
                seg.put_annotation("http.method",  request.method)
                seg.put_annotation("http.url",     str(request.url))
                seg.put_annotation("request_id",   request_id)

                start = time.time()
                response: Response = await call_next(request)
                duration_ms = round((time.time() - start) * 1000, 2)

                seg.put_annotation("http.status", response.status_code)
                seg.put_annotation("duration_ms", duration_ms)

                trace_id = seg.trace_id
        except Exception:
            # X-Ray not available — still process request
            start = time.time()
            response = await call_next(request)
            duration_ms = round((time.time() - start) * 1000, 2)
            trace_id = f"demo-{request_id[:8]}"

        # Inject trace headers
        response.headers["X-Trace-Id"]   = trace_id
        response.headers["X-Request-Id"] = request_id
        return response


# =====================================================
# 3. RATE LIMIT MIDDLEWARE
# =====================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Enforces per-user token bucket rate limits.
    Returns 429 with Retry-After header when limit is exceeded.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for public paths
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # Get user identity (set by JWTAuthMiddleware)
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            # Not authenticated — let JWTAuthMiddleware handle it
            return await call_next(request)

        limiter = get_rate_limiter()
        allowed, info = await limiter.check(user_id, request.url.path)

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error":   "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please slow down.",
                    "retry_after_seconds": info["reset_in_seconds"],
                },
                headers={
                    "X-RateLimit-Limit":     str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset":     info["reset_at"],
                    "Retry-After":           str(int(info["reset_in_seconds"]) + 1),
                },
            )

        response = await call_next(request)

        # Add rate limit headers to all responses
        response.headers["X-RateLimit-Limit"]     = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"]     = info["reset_at"]
        return response


# =====================================================
# 4. SECURITY HEADERS MIDDLEWARE
# =====================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to every response.
    These are basic hygiene that every production app should have.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"]    = "nosniff"
        response.headers["X-Frame-Options"]            = "DENY"
        response.headers["X-XSS-Protection"]           = "1; mode=block"
        response.headers["Strict-Transport-Security"]  = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"]            = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"]    = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://*.amazonaws.com"
        )
        # Remove server fingerprint
        response.headers.pop("server", None)
        response.headers.pop("x-powered-by", None)
        return response
