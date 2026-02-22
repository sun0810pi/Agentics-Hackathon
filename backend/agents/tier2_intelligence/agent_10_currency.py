"""Agent 10: Multi-Currency - FX conversion and risk"""
from agents.base import BaseAgent
class Agent10Currency(BaseAgent):
    agent_id = 10
    agent_name = "Multi-Currency"
    tier = "ML Intelligence"
    FX_RATES = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27, "VND": 0.000041, "JPY": 0.0067}
    async def _execute(self, invoice_data, context):
        ocr_fields = context.get("results", {}).get(0, {}).get("invoice_fields", {})
        currency = ocr_fields.get("currency", "USD")
        flags = [] if currency in self.FX_RATES else ["UNKNOWN_CURRENCY"]
        return {"currency_detected": currency, "fx_rate_usd": self.FX_RATES.get(currency, 1.0), "currency_risk": "LOW"}, flags, 0.93
