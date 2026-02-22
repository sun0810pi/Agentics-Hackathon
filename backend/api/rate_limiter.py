"""
backend/api/rate_limiter.py
============================
Per-user Token Bucket Rate Limiter.

Algorithm:
- Mỗi user có 1 bucket với max N tokens
- Mỗi request tiêu 1-2 tokens (tuỳ endpoint)
- Tokens refill liên tục theo thời gian
- Bucket rỗng → 429 Too Many Requests

Thread-safe với asyncio.Lock cho single instance.
Cần Redis để safe khi horizontal scaling (nhiều Lambda instances).
"""

import time, asyncio, logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    max_tokens:  float
    refill_rate: float          # tokens/second
    tokens:      float
    last_refill: float = field(default_factory=time.time)

    def consume(self, cost: float = 1.0) -> Tuple[bool, float]:
        """Trả về (allowed, tokens_remaining)."""
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True, self.tokens
        return False, self.tokens

    def _refill(self) -> None:
        now     = time.time()
        added   = (now - self.last_refill) * self.refill_rate
        self.tokens      = min(self.max_tokens, self.tokens + added)
        self.last_refill = now

    @property
    def reset_in_seconds(self) -> float:
        if self.tokens >= self.max_tokens: return 0.0
        return (self.max_tokens - self.tokens) / self.refill_rate


class RateLimiter:
    """
    In-memory per-user rate limiter.
    Default: 15 tokens max, 10 tokens/minute refill.
    Heavy endpoints (/api/analyze) cost 2 tokens.
    """

    ENDPOINT_COSTS: Dict[str, float] = {
        "/api/analyze":         2.0,
        "/api/metrics":         1.0,
        "/api/invoices":        1.0,
        "/api/fraud-scenarios": 1.0,
        "/api/audit-logs":      1.0,
        "/api/agents/status":   0.5,
        "/api/feedback":        1.0,
        "/health":              0.0,
    }

    def __init__(self, max_tokens: float = 15.0, refill_rate: float = 10.0/60.0,
                 cleanup_interval: int = 300):
        self.max_tokens       = max_tokens
        self.refill_rate      = refill_rate
        self.cleanup_interval = cleanup_interval
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock            = asyncio.Lock()
        self._last_cleanup    = time.time()

    async def check(self, user_id: str, endpoint: str = "/api/analyze") -> Tuple[bool, dict]:
        async with self._lock:
            self._maybe_cleanup()
            if user_id not in self._buckets:
                self._buckets[user_id] = TokenBucket(
                    max_tokens=self.max_tokens,
                    refill_rate=self.refill_rate,
                    tokens=self.max_tokens,
                )
            bucket = self._buckets[user_id]
            cost   = self.ENDPOINT_COSTS.get(endpoint, 1.0)

            if cost == 0.0:
                return True, self._info(bucket, user_id)

            allowed, remaining = bucket.consume(cost)
            if not allowed:
                logger.warning(f"Rate limit exceeded user={user_id} endpoint={endpoint}")
            return allowed, self._info(bucket, user_id, remaining)

    def _info(self, bucket: TokenBucket, user_id: str, remaining: float = None) -> dict:
        r = remaining if remaining is not None else bucket.tokens
        return {
            "user_id":           user_id,
            "limit":             int(self.max_tokens),
            "remaining":         max(0, int(r)),
            "reset_in_seconds":  round(bucket.reset_in_seconds, 1),
            "reset_at":          datetime.fromtimestamp(
                                     time.time() + bucket.reset_in_seconds,
                                     tz=timezone.utc).isoformat(),
        }

    def _maybe_cleanup(self) -> None:
        now = time.time()
        if now - self._last_cleanup < self.cleanup_interval: return
        stale = [uid for uid, b in self._buckets.items() if b.last_refill < now - self.cleanup_interval*2]
        for uid in stale: del self._buckets[uid]
        if stale: logger.debug(f"Rate limiter: cleaned {len(stale)} stale buckets")
        self._last_cleanup = now

    def get_stats(self) -> dict:
        return {"active_users": len(self._buckets), "max_tokens": self.max_tokens,
                "refill_rate": self.refill_rate, "endpoint_costs": self.ENDPOINT_COSTS}


# Singleton
import os
_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter(
            max_tokens=float(os.getenv("RATE_LIMIT_MAX_TOKENS", "15")),
            refill_rate=float(os.getenv("RATE_LIMIT_REFILL_RATE", str(10/60))),
        )
    return _limiter
