"""Agent 1: PII Preprocessor - Masks PII for GDPR compliance"""
import re
from agents.base import BaseAgent
from typing import Dict, Any, List, Tuple

class Agent1PII(BaseAgent):
    agent_id = 1
    agent_name = "PII Preprocessor"
    tier = "Core Detection"

    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\+?[\d\s\-\(\)]{10,15}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    }

    async def _execute(self, invoice_data: Dict, context: Dict) -> Tuple[Dict, List[str], float]:
        raw_text = context.get("results", {}).get(0, {}).get("raw_text", "")
        flags = []
        pii_found = {}

        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, raw_text)
            if matches:
                pii_found[pii_type] = len(matches)
                flags.append(f"PII_DETECTED_{pii_type.upper()}")

        # Mask PII in raw text (replace with [REDACTED])
        masked_text = raw_text
        for pattern in self.PII_PATTERNS.values():
            masked_text = re.sub(pattern, "[REDACTED]", masked_text)

        return {
            "pii_types_found": list(pii_found.keys()),
            "pii_count": sum(pii_found.values()),
            "masked_text": masked_text,
            "gdpr_compliant": True,
        }, flags, 0.95
