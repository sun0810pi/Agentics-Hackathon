"""Agent 2: Decimal Matcher - Validates invoice amounts vs PO data"""
from agents.base import BaseAgent
from typing import Dict, Any, List, Tuple
import re

class Agent2Decimal(BaseAgent):
    agent_id = 2
    agent_name = "Decimal Matcher"
    tier = "Core Detection"

    async def _execute(self, invoice_data: Dict, context: Dict) -> Tuple[Dict, List[str], float]:
        flags = []
        ocr_data = context.get("results", {}).get(0, {}).get("invoice_fields", {})
        amount_str = ocr_data.get("amount_total", "")
        amount = None
        discrepancy = False

        try:
            if amount_str:
                cleaned = re.sub(r'[^\d.]', '', str(amount_str))
                amount = float(cleaned)
                # Check for suspicious round numbers (fraud indicator)
                if amount > 10000 and amount % 1000 == 0:
                    flags.append("SUSPICIOUS_ROUND_AMOUNT")
                # Check for micro-amounts (test invoice?)
                if amount < 1.0:
                    flags.append("SUSPICIOUSLY_LOW_AMOUNT")
                # Check for extremely large amounts
                if amount > 1_000_000:
                    flags.append("EXTREMELY_LARGE_AMOUNT")
        except (ValueError, TypeError):
            flags.append("INVALID_AMOUNT_FORMAT")

        return {
            "amount_parsed": amount,
            "amount_valid": amount is not None and amount > 0,
            "discrepancy_detected": discrepancy,
        }, flags, 0.92 if amount else 0.3
