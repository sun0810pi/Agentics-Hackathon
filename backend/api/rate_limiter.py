"""
backend/api/rate_limiter.py
============================
Per-user token bucket rate limiter.

This is a TOP 1% feature — not just WAF-level limiting, but
per-identity application-level limiting with token bucket algorithm.

Token Bucket Algorithm:
- Each user has a bucket with max N tokens
- Each request consumes 1 token
- Tokens refill at rate R per second
- If bucket empty → 429 Too Many Requests
"""

import time
import asyncio
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """
    A single user's token bucket.

    max_tokens:   Maximum capacity (burst limit)
    refill_rate:  Tokens added per second
    tokens:       Current token count
    last_refill:  Timestamp of last refill
    """
    max_tokens:  float
    refill_rate: float
    tokens:      float
    last_refill: float = field(default_factory=time.time)

    def consume(self, tokens: float = 1.0) -> Tuple[bool, float]:
        """
        Try to consume `tokens` from the bucket.

        Returns:
            (allowed: bool, tokens_remaining: float)
        """
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, self.tokens
        return False, self.tokens

    def _refill(self) -> None:
        """Add tokens based on elapsed time since last refill."""
        now = time.time()
        elapsed = now - self.last_refill
        added = elapsed * self.refill_rate
        self.tokens = min(self.max_tokens, self.tokens + added)
        self.last_refill = now

    @property
    def reset_at(self) -> float:
        """Seconds until bucket is full (for Retry-After header)."""
        if self.tokens >= self.max_tokens:
            return 0.0
        needed = self.max_tokens - self.tokens
        return needed / self.refill_rate


class RateLimiter:
    """
    In-memory rate limiter.

    For production scale: swap the dict for Redis using the same interface.
    The logic here is identical — only storage changes.

    Default config:
        - 10 requests per 60-second window per user
        - Burst of 15 allowed (token bucket smoothing)
        - /api/analyze endpoint costs 2 tokens (heavy operation)
        - /api/metrics  endpoint costs 1 token
    """

    # Endpoint cost table — heavier operations cost more tokens
    ENDPOINT_COSTS: Dict[str, float] = {
        "/api/analyze":         2.0,
        "/api/metrics":         1.0,
        "/api/invoices":        1.0,
        "/api/fraud-scenarios": 1.0,
        "/api/audit-logs":      1.0,
        "/api/agents/status":   0.5,
        "/health":              0.0,  # health checks are free
    }

    def __init__(
        self,
        max_tokens:  float = 15.0,
        refill_rate: float = 10.0 / 60.0,  # 10 requests / 60 seconds
        cleanup_interval: int = 300,         # clean stale buckets every 5 min
    ):
        self.max_tokens  = max_tokens
        self.refill_rate = refill_rate
        self.cleanup_interval = cleanup_interval
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = asyncio.Lock()
        self._last_cleanup = time.time()

    def _get_or_create_bucket(self, user_id: str) -> TokenBucket:
        """Get existing bucket or create new full bucket for user."""
        if user_id not in self._buckets:
            self._buckets[user_id] = TokenBucket(
                max_tokens=self.max_tokens,
                refill_rate=self.refill_rate,
                tokens=self.max_tokens,  # start full
            )
        return self._buckets[user_id]

    async def check(
        self,
        user_id: str,
        endpoint: str = "/api/analyze",
    ) -> Tuple[bool, Dict]:
        """
        Check if user is within rate limit.

        Returns:
            (allowed: bool, info: dict with limit headers)
        """
        async with self._lock:
            self._maybe_cleanup()
            bucket = self._get_or_create_bucket(user_id)
            cost = self.ENDPOINT_COSTS.get(endpoint, 1.0)

            if cost == 0.0:
                return True, self._build_info(bucket, user_id)

            allowed, remaining = bucket.consume(cost)
            info = self._build_info(bucket, user_id, remaining)

            if not allowed:
                logger.warning(
                    f"Rate limit exceeded: user={user_id} endpoint={endpoint} "
                    f"tokens={remaining:.2f}"
                )
            return allowed, info

    def _build_info(
        self,
        bucket: TokenBucket,
        user_id: str,
        remaining: Optional[float] = None,
    ) -> Dict:
        if remaining is None:
            remaining = bucket.tokens
        return {
            "user_id":         user_id,
            "limit":           int(self.max_tokens),
            "remaining":       max(0, int(remaining)),
            "reset_in_seconds": round(bucket.reset_at, 1),
            "reset_at":        datetime.utcfromtimestamp(
                                   time.time() + bucket.reset_at
                               ).isoformat(),
        }

    def _maybe_cleanup(self) -> None:
        """Remove stale buckets to prevent memory leak."""
        now = time.time()
        if now - self._last_cleanup < self.cleanup_interval:
            return
        stale_cutoff = now - (self.cleanup_interval * 2)
        stale = [
            uid for uid, b in self._buckets.items()
            if b.last_refill < stale_cutoff
        ]
        for uid in stale:
            del self._buckets[uid]
        if stale:
            logger.debug(f"Rate limiter cleaned {len(stale)} stale buckets")
        self._last_cleanup = now

    def get_stats(self) -> Dict:
        """Return current limiter stats (for admin endpoint)."""
        return {
            "active_users":  len(self._buckets),
            "max_tokens":    self.max_tokens,
            "refill_rate":   self.refill_rate,
            "endpoint_costs": self.ENDPOINT_COSTS,
        }


# ── Singleton instance ────────────────────────────────
_rate_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        import os
        _rate_limiter = RateLimiter(
            max_tokens=float(os.getenv("RATE_LIMIT_MAX_TOKENS", "15")),
            refill_rate=float(os.getenv("RATE_LIMIT_REFILL_RATE", str(10/60))),
        )
    return _rate_limiter
