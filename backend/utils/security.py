"""
backend/utils/security.py + validators.py
==========================================
Security utilities and input validation for the backend.
"""

import re
import hashlib
import hmac
import os
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


# =====================================================
# SECURITY UTILITIES
# =====================================================

def hash_sensitive(value: str) -> str:
    """One-way hash for sensitive values (for logging/audit)."""
    return hashlib.sha256(value.encode()).hexdigest()[:16] + "..."


def constant_time_compare(a: str, b: str) -> bool:
    """Timing-safe string comparison. Prevents timing attacks."""
    return hmac.compare_digest(a.encode(), b.encode())


def sanitize_for_log(text: str, max_len: int = 100) -> str:
    """Clean string for safe inclusion in log messages."""
    cleaned = re.sub(r'[^\w\s\-\.\,\@]', '', str(text))
    return cleaned[:max_len]


# =====================================================
# INPUT VALIDATORS
# =====================================================

class InputValidator:
    """
    Server-side input validation.
    ALWAYS validate on the server even if frontend also validates.
    Uses WHITELIST approach (allow known-good), not blacklist.
    """

    EMAIL_RE    = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
    INV_ID_RE   = re.compile(r'^[A-Z0-9\-]{3,50}$')
    FILENAME_RE = re.compile(r'^[a-zA-Z0-9._\-\s]{1,255}$')
    VENDOR_RE   = re.compile(r'^[a-zA-Z0-9\s\.\,\-&\']{1,200}$')

    @classmethod
    def validate_email(cls, email: str) -> bool:
        return bool(cls.EMAIL_RE.match(email))

    @classmethod
    def validate_invoice_id(cls, invoice_id: str) -> bool:
        return bool(cls.INV_ID_RE.match(invoice_id.upper()))

    @classmethod
    def validate_filename(cls, filename: str) -> bool:
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        allowed = {'.pdf', '.png', '.jpg', '.jpeg'}
        return (
            bool(cls.FILENAME_RE.match(filename)) and
            any(filename.lower().endswith(ext) for ext in allowed)
        )

    @classmethod
    def validate_amount(cls, amount: Any) -> Optional[float]:
        """Return float if valid, None if not."""
        try:
            v = float(amount)
            if v < 0 or v > 10_000_000:
                return None
            return round(v, 2)
        except (TypeError, ValueError):
            return None

    @classmethod
    def validate_mode(cls, mode: str) -> bool:
        return mode in ("full", "fast", "demo")

    @classmethod
    def detect_injection(cls, text: str) -> bool:
        """
        Detect common injection patterns.
        Returns True if suspicious content found.
        This is an additional layer on top of parameterized queries.
        """
        patterns = [
            r"('|\")(\s)*(OR|AND)(\s)+",          # SQL OR/AND injection
            r"(DROP|DELETE|INSERT|UPDATE)(\s)+",    # SQL DDL/DML
            r"<script[\s\S]*?>[\s\S]*?<\/script>", # XSS script tag
            r"javascript\s*:",                      # JavaScript URL
            r"\.\./",                               # Path traversal
            r";\s*(ls|cat|rm|wget|curl)\s",        # Command injection
        ]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Injection pattern detected: {sanitize_for_log(text[:50])}")
                return True
        return False


validator = InputValidator()
