"""backend/utils/security.py + validators.py"""
import re, hashlib, hmac, logging
from typing import Any, Optional
logger = logging.getLogger(__name__)

# ── Security helpers ──────────────────────────────────────
def hash_sensitive(v: str) -> str:
    return hashlib.sha256(v.encode()).hexdigest()[:16] + "..."

def constant_time_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())

def sanitize_log(text: str, max_len=100) -> str:
    return re.sub(r'[^\w\s\-\.\,\@]', '', str(text))[:max_len]

# ── Input validators (whitelist approach) ─────────────────
class InputValidator:
    EMAIL_RE    = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
    INV_ID_RE   = re.compile(r'^[A-Z0-9\-]{3,50}$')
    FILENAME_RE = re.compile(r'^[a-zA-Z0-9._\-\s]{1,255}$')

    @classmethod
    def email(cls, v: str) -> bool: return bool(cls.EMAIL_RE.match(v))
    @classmethod
    def invoice_id(cls, v: str) -> bool: return bool(cls.INV_ID_RE.match(v.upper()))
    @classmethod
    def filename(cls, v: str) -> bool:
        if any(c in v for c in ('..','/','\\')):  return False
        return bool(cls.FILENAME_RE.match(v)) and any(v.lower().endswith(e) for e in ('.pdf','.png','.jpg','.jpeg'))
    @classmethod
    def amount(cls, v: Any) -> Optional[float]:
        try:
            f = float(v)
            return round(f,2) if 0 <= f <= 10_000_000 else None
        except: return None
    @classmethod
    def detect_injection(cls, text: str) -> bool:
        patterns = [r"('|\")\s*(OR|AND)\s+",r"(DROP|DELETE|INSERT|UPDATE)\s+",r"<script[\s\S]*?>",r"javascript\s*:",r"\.\./",r";\s*(ls|cat|rm|wget|curl)\s"]
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                logger.warning(f"Injection detected: {sanitize_log(text[:50])}"); return True
        return False

validator = InputValidator()
