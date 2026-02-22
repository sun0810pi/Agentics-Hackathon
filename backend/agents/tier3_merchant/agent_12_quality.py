"""Agent 12: Quality Inspector - Validates extraction completeness"""
from agents.base import BaseAgent
class Agent12Quality(BaseAgent):
    agent_id = 12
    agent_name = "Quality Inspector"
    tier = "Merchant Success"
    REQUIRED = ["invoice_number", "vendor_name", "amount_total", "invoice_date"]
    async def _execute(self, invoice_data, context):
        fields = context.get("results", {}).get(0, {}).get("invoice_fields", {})
        missing = [f for f in self.REQUIRED if not fields.get(f)]
        flags = [f"MISSING_FIELD_{f.upper()}" for f in missing]
        score = (len(self.REQUIRED) - len(missing)) / len(self.REQUIRED)
        return {"completeness_score": round(score, 2), "missing_fields": missing, "quality_grade": "A" if score >= 0.9 else "B"}, flags, score
