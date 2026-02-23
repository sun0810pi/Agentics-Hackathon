"""
backend/api/rate_limiter.py
============================
Per-user Token Bucket Rate Limiter.

PERF FIX:
  - Old: asyncio.Lock() held for the ENTIRE check() including cleanup loop
  - New: fine-grained locking — only per-bucket dict access is locked
  - Cleanup runs with a separate short lock, non-blocking for other users
  - Per-bucket update is now O(1) instead of holding global lock

Thread-safe for asyncio (single event loop). Needs Redis for multi-instance.
"""

import time, asyncio, logging, os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    max_tokens:  float
    refill_rate: float   # tokens/second
    tokens:      float
    last_refill: float = field(default_factory=time.time)

    def consume(self, cost: float = 1.0) -> Tuple[bool, float]:
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True, self.tokens
        return False, self.tokens

    def _refill(self) -> None:
        now          = time.time()
        added        = (now - self.last_refill) * self.refill_rate
        self.tokens  = min(self.max_tokens, self.tokens + added)
        self.last_refill = now

    @property
    def reset_in_seconds(self) -> float:
        if self.tokens >= self.max_tokens:
            return 0.0
        return (self.max_tokens - self.tokens) / self.refill_rate


class RateLimiter:
    """
    In-memory per-user token bucket.
    Default: 15 tokens max, 10 tokens/minute refill.
    /api/analyze costs 2 tokens.
    """

    ENDPOINT_COSTS: Dict[str, float] = {
        "/api/analyze":         2.0,
        "/api/metrics":         1.0,
        "/api/invoices":        1.0,
        "/api/fraud-scenarios": 1.0,
        "/api/audit-logs":      1.0,
        "/api/agents/status":   0.5,
        "/api/feedback":        1.0,
        "/api/test-attack":     0.5,
        "/api/xray-traces":     0.5,
        "/health":              0.0,
    }

    def __init__(
        self,
        max_tokens:       float = 15.0,
        refill_rate:      float = 10.0 / 60.0,
        cleanup_interval: int   = 300,
    ):
        self.max_tokens       = max_tokens
        self.refill_rate      = refill_rate
        self.cleanup_interval = cleanup_interval
        self._buckets:        Dict[str, TokenBucket] = {}
        # PERF: separate lock per bucket dict operation (not one big global lock)
        self._dict_lock       = asyncio.Lock()   # only for creating new buckets
        self._cleanup_lock    = asyncio.Lock()   # only for cleanup
        self._last_cleanup    = time.time()

    async def check(self, user_id: str, endpoint: str = "/api/analyze") -> Tuple[bool, dict]:
        cost = self.ENDPOINT_COSTS.get(endpoint, 1.0)

        # Free endpoints: no lock needed at all
        if cost == 0.0:
            bucket = await self._get_or_create_bucket(user_id)
            return True, self._info(bucket, user_id)

        # Ensure bucket exists (dict_lock only if bucket missing)
        bucket = await self._get_or_create_bucket(user_id)

        # PERF: bucket.consume() is not shared across coroutines (asyncio = single-threaded)
        # No lock needed for consume — only one coroutine runs at a time in asyncio
        allowed, remaining = bucket.consume(cost)

        if not allowed:
            logger.warning(f"Rate limit exceeded user={user_id} endpoint={endpoint}")

        # Cleanup check — async, non-blocking (try_acquire pattern)
        if not self._cleanup_lock.locked():
            asyncio.ensure_future(self._maybe_cleanup())

        return allowed, self._info(bucket, user_id, remaining)

    async def _get_or_create_bucket(self, user_id: str) -> TokenBucket:
        if user_id in self._buckets:
            return self._buckets[user_id]
        # Only lock for new bucket creation
        async with self._dict_lock:
            if user_id not in self._buckets:
                self._buckets[user_id] = TokenBucket(
                    max_tokens=self.max_tokens,
                    refill_rate=self.refill_rate,
                    tokens=self.max_tokens,
                )
        return self._buckets[user_id]

    async def _maybe_cleanup(self) -> None:
        now = time.time()
        if now - self._last_cleanup < self.cleanup_interval:
            return
        async with self._cleanup_lock:
            if now - self._last_cleanup < self.cleanup_interval:
                return   # double-check after acquiring
            stale = [
                uid for uid, b in self._buckets.items()
                if b.last_refill < now - self.cleanup_interval * 2
            ]
            for uid in stale:
                del self._buckets[uid]
            self._last_cleanup = now
            if stale:
                logger.debug(f"Rate limiter: cleaned {len(stale)} stale buckets")

    def _info(self, bucket: TokenBucket, user_id: str, remaining: Optional[float] = None) -> dict:
        r = remaining if remaining is not None else bucket.tokens
        return {
            "user_id":          user_id,
            "limit":            int(self.max_tokens),
            "remaining":        max(0, int(r)),
            "reset_in_seconds": round(bucket.reset_in_seconds, 1),
            "reset_at":         datetime.fromtimestamp(
                                    time.time() + bucket.reset_in_seconds,
                                    tz=timezone.utc,
                                ).isoformat(),
        }

    def get_stats(self) -> dict:
        return {
            "active_users":   len(self._buckets),
            "max_tokens":     self.max_tokens,
            "refill_rate":    self.refill_rate,
            "endpoint_costs": self.ENDPOINT_COSTS,
        }


# ── Singleton ─────────────────────────────────────────────
_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter(
            max_tokens=float(os.getenv("RATE_LIMIT_MAX_TOKENS", "15")),
            refill_rate=float(os.getenv("RATE_LIMIT_REFILL_RATE", str(10 / 60))),
        )
    return _limiter
