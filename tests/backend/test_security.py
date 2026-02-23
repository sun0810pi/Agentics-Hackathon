"""
tests/backend/test_security.py
================================
Security tests: SQL injection, XSS, path traversal, rate limiting.
Run: cd backend && pytest ../tests/backend/test_security.py -v
"""
import sys, os, pytest, asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from utils.security import validator
from api.rate_limiter import RateLimiter


# ── Input validation ──────────────────────────────────────

def test_sql_injection_detected():
    payloads = [
        "1' OR '1'='1",
        "admin'--",
        "1; DROP TABLE users--",
        "' UNION SELECT * FROM users--",
    ]
    for p in payloads:
        assert validator.detect_injection(p), f"Should detect SQL injection: {p!r}"


def test_xss_detected():
    payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
    ]
    for p in payloads:
        assert validator.detect_injection(p), f"Should detect XSS: {p!r}"


def test_path_traversal_detected():
    payloads = ["../../../etc/passwd", "....//etc/passwd"]
    for p in payloads:
        assert validator.detect_injection(p), f"Should detect path traversal: {p!r}"


def test_command_injection_detected():
    payloads = ["; ls -la", "| cat /etc/passwd", "; rm -rf /"]
    for p in payloads:
        assert validator.detect_injection(p), f"Should detect command injection: {p!r}"


def test_safe_inputs_not_flagged():
    safe = ["TechCorp Inc", "INV-2026-0001", "Professional Services", "John Smith", "$5,000.00"]
    for s in safe:
        assert not validator.detect_injection(s), f"Safe input incorrectly flagged: {s!r}"


def test_invoice_id_whitelist():
    valid   = ["INV-2026-0001", "ABC123", "TEST-001"]
    invalid = ["../etc", "<script>", "'; DROP TABLE", "INV 2026 0001", ""]
    for v in valid:   assert validator.invoice_id(v),     f"Should be valid: {v!r}"
    for v in invalid: assert not validator.invoice_id(v), f"Should be invalid: {v!r}"


def test_filename_path_traversal():
    assert not validator.filename("../../../etc/passwd")
    assert not validator.filename("/etc/passwd")
    assert not validator.filename("..\\..\\windows\\system32")
    assert not validator.filename("invoice.exe")           # wrong extension
    assert validator.filename("invoice_2026.pdf")
    assert validator.filename("my-invoice.png")


def test_amount_validation():
    assert validator.amount(5000)   == 5000.0
    assert validator.amount(-100)   is None
    assert validator.amount(99_999_999) is None
    assert validator.amount("abc") is None
    assert validator.amount(0)     == 0.0
    assert validator.amount("1234.56") == 1234.56


# ── Rate limiter ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_rate_limiter_allows_within_limit():
    limiter = RateLimiter(max_tokens=10, refill_rate=1.0)
    for _ in range(5):
        allowed, info = await limiter.check("user1", "/api/metrics")
        assert allowed, "Should be allowed within limit"
        assert info["remaining"] >= 0


@pytest.mark.asyncio
async def test_rate_limiter_blocks_when_exceeded():
    limiter = RateLimiter(max_tokens=3, refill_rate=0.001)
    user = "test-user-block"
    results = []
    for _ in range(10):
        allowed, _ = await limiter.check(user, "/api/analyze")   # costs 2 tokens
        results.append(allowed)
    assert any(not r for r in results), "Rate limiter should block after tokens exhausted"


@pytest.mark.asyncio
async def test_rate_limiter_health_path_free():
    """FIX: /health path costs 0 tokens — should never be rate limited."""
    limiter = RateLimiter(max_tokens=1, refill_rate=0.001)
    user    = "health-test-user"
    # Exhaust the bucket first
    for _ in range(5):
        await limiter.check(user, "/api/analyze")
    # /health must still be allowed (cost = 0.0)
    allowed, info = await limiter.check(user, "/health")
    assert allowed, "/health should never be rate limited (cost=0)"
    assert info["remaining"] >= 0   # bucket state returned correctly


@pytest.mark.asyncio
async def test_rate_limiter_users_are_independent():
    limiter = RateLimiter(max_tokens=4, refill_rate=0.001)
    # Exhaust user A
    for _ in range(10):
        await limiter.check("user-A", "/api/analyze")
    # user B should still be fully allowed
    allowed, info = await limiter.check("user-B", "/api/analyze")
    assert allowed, "Different users should have independent buckets"
    assert info["remaining"] >= 0


@pytest.mark.asyncio
async def test_rate_limiter_returns_retry_info():
    """When blocked, response should include reset info."""
    limiter = RateLimiter(max_tokens=2, refill_rate=0.001)
    user    = "retry-user"
    # Drain bucket
    for _ in range(10):
        allowed, info = await limiter.check(user, "/api/analyze")
    # After exhaustion, info should contain retry metadata
    assert "reset_in_seconds" in info
    assert "reset_at"         in info
    assert "limit"            in info
    assert info["limit"] == 2


@pytest.mark.asyncio
async def test_rate_limiter_concurrent_safety():
    """Multiple concurrent requests for same user should not over-consume."""
    limiter = RateLimiter(max_tokens=10, refill_rate=1.0)
    user    = "concurrent-user"
    tasks   = [limiter.check(user, "/api/metrics") for _ in range(10)]
    results = await asyncio.gather(*tasks)
    allowed_count = sum(1 for allowed, _ in results if allowed)
    assert allowed_count <= 10, "Should not allow more than max_tokens"
    assert allowed_count >  0,  "Some requests should succeed"
