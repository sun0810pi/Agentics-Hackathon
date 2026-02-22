# =====================================================
# backend/utils/validators.py
# Server-side input validation
# ALWAYS validate on backend even if frontend validates!
# Uses WHITELIST approach (not blacklist)
# =====================================================

import re
import logging
from typing import Optional, Tuple

import bleach

logger = logging.getLogger(__name__)

# Allowed file MIME types (whitelist)
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}

# Max file size (50MB in bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Safe string patterns (whitelist approach - only allow known-good chars)
SAFE_INVOICE_NUMBER = re.compile(r'^[A-Za-z0-9\-/]+$')
SAFE_VENDOR_NAME = re.compile(r'^[A-Za-z0-9\s\.\,\-\&\']+$')
SAFE_EMAIL = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

# SQL injection patterns to detect (for logging/alerting only - we use parameterized queries)
SQL_INJECTION_PATTERNS = [
    r"('|--|;|\/\*|\*\/|xp_|exec\s|union\s+select|drop\s+table)",
]

# XSS patterns to detect (for logging/alerting only - we use bleach sanitization)
XSS_PATTERNS = [
    r"<script[^>]*>",
    r"javascript\s*:",
    r"on\w+\s*=",
    r"<iframe",
    r"<svg.*onload",
]


def validate_file(file_bytes: bytes, content_type: str, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.

    Returns:
        (valid: bool, error_message: Optional[str])
    """
    # Check file size
    if len(file_bytes) > MAX_FILE_SIZE:
        return False, f"File too large: {len(file_bytes) / 1024 / 1024:.1f}MB (max 50MB)"

    # Check MIME type (whitelist)
    if content_type not in ALLOWED_MIME_TYPES:
        return False, f"File type not allowed: {content_type}"

    # Check file extension (defense in depth)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    allowed_extensions = {"pdf", "png", "jpg", "jpeg"}
    if ext not in allowed_extensions:
        return False, f"File extension not allowed: .{ext}"

    # Check PDF magic bytes (prevent MIME spoofing)
    if content_type == "application/pdf":
        if not file_bytes.startswith(b"%PDF"):
            return False, "File claims to be PDF but is not a valid PDF"

    # Check PNG magic bytes
    if content_type == "image/png":
        if not file_bytes.startswith(b"\x89PNG"):
            return False, "File claims to be PNG but is not a valid PNG"

    return True, None


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize a string input:
    1. Strip whitespace
    2. Truncate to max length
    3. Remove HTML tags with bleach
    4. Log if injection patterns detected
    """
    if not isinstance(value, str):
        return ""

    value = value.strip()[:max_length]

    # Detect (but don't block - we use parameterized queries and bleach)
    _detect_injection_attempt(value)

    # Sanitize HTML (bleach strips all tags by default)
    value = bleach.clean(value, tags=[], strip=True)

    return value


def _detect_injection_attempt(value: str) -> bool:
    """
    Detect if value looks like an injection attempt.
    Log for security monitoring. We don't block here because:
    - SQL: We use parameterized queries (injection impossible)
    - XSS: We use bleach (sanitized before output)
    But we DO log for CloudWatch alerting.
    """
    value_lower = value.lower()

    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value_lower, re.IGNORECASE):
            logger.warning(f"SQL injection pattern detected in input: {value[:50]}...")
            return True

    for pattern in XSS_PATTERNS:
        if re.search(pattern, value_lower, re.IGNORECASE):
            logger.warning(f"XSS pattern detected in input: {value[:50]}...")
            return True

    return False


def validate_user_id(user_id: str) -> bool:
    """Validate user ID format (UUID from Cognito)."""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(user_id))


def validate_pagination(page: int, page_size: int) -> Tuple[int, int]:
    """Clamp pagination to safe values."""
    page = max(1, page)
    page_size = max(1, min(page_size, 1000))
    return page, page_size
