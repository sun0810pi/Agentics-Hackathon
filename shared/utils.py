# shared/utils.py - Utilities shared between frontend and backend
import hashlib

def generate_audit_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()
