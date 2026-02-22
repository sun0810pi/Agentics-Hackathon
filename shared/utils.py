"""
shared/utils.py
================
Utility functions used by both frontend and backend.
"""

import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict


def compute_hash(data: Dict[str, Any]) -> str:
    """Compute SHA-256 hash of a dict (for audit trail)."""
    payload = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def is_valid_invoice_id(invoice_id: str) -> bool:
    return bool(re.match(r"^[A-Z0-9\-]{3,50}$", invoice_id))


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", email))


def risk_level_from_score(score: float) -> str:
    if score >= 85: return "CRITICAL"
    if score >= 70: return "HIGH"
    if score >= 30: return "MEDIUM"
    return "LOW"


def decision_from_score(score: float) -> str:
    if score >= 70: return "BLOCK"
    if score >= 30: return "REVIEW"
    return "APPROVE"


def format_currency(amount: float, currency: str = "USD") -> str:
    symbols = {"USD": "$", "EUR": "€", "VND": "₫", "GBP": "£", "JPY": "¥"}
    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:,.2f}"


def now_iso() -> str:
    return datetime.utcnow().isoformat()
