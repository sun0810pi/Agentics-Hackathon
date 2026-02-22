"""Agents 9-16: Tier 2 (remaining), Tier 3, Tier 4"""
import random, logging
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier
logger = logging.getLogger(__name__)

# ── Tier 2 ────────────────────────────────────────────────
class Agent9Learning(BaseAgent):
    agent_id = 9; agent_name = "Continuous Learning"; tier = AgentTier.INTELLIGENCE
    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        return AgentOutput(9, self.agent_name, "COMPLETED", 0, 1.0, findings={
            "model_version": "v2.1.0", "last_retrain": "2026-02-20T10:00:00Z",
            "accuracy_trend": "+0.3% this week", "feedback_processed": 0})

class Agent10Currency(BaseAgent):
    agent_id = 10; agent_name = "Multi-Currency"; tier = AgentTier.INTELLIGENCE
    FX = {"USD":1.0,"EUR":1.08,"VND":0.000040,"GBP":1.27,"JPY":0.0067}
    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        currency = ctx.extracted.get("currency","USD"); total = float(ctx.extracted.get("total_amount",0))
        usd = round(total * self.FX.get(currency,1.0), 2)
        flags = ["LARGE_FOREIGN_CURRENCY_TRANSACTION"] if currency != "USD" and usd > 100_000 else []
        if flags: ctx.fraud_flags.append("LARGE_FOREIGN_CURRENCY")
        return AgentOutput(10, self.agent_name, "COMPLETED", 0, 0.99, findings={
            "original_currency": currency, "original_amount": total,
            "usd_equivalent": usd, "fx_rate": self.FX.get(currency,1.0), "fx_risk": bool(flags)}, flags=flags)

# ── Tier 3 ────────────────────────────────────────────────
class Agent11Merchant(BaseAgent):
    agent_id = 11; agent_name = "Merchant Advisor"; tier = AgentTier.MERCHANT
    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        return AgentOutput(11, self.agent_name, "COMPLETED", 0, 0.88, findings={
            "vendor_id": ctx.extracted.get("vendor_id","unknown"),
            "vendor_risk_score": random.randint(10,85), "total_invoices": random.randint(5,200),
            "fraud_rate": round(random.uniform(0,0.15),3), "avg_invoice_amount": round(random.uniform(1000,20000),2),
            "relationship_months": random.randint(1,60),
            "recommendation": "Monitor closely" if random.random()>0.7 else "Trusted vendor"})

class Agent12Quality(BaseAgent):
    agent_id = 12; agent_name = "Quality Inspector"; tier = AgentTier.MERCHANT
    REQUIRED = ["invoice_number","vendor_name","total_amount","invoice_date"]
    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        missing = [f for f in self.REQUIRED if not ctx.extracted.get(f)]
        conf = float(ctx.extracted.get("ocr_confidence",0))
        score = round(((len(self.REQUIRED)-len(missing))/len(self.REQUIRED))*100*conf,1)
        if missing: ctx.fraud_flags.append("MISSING_REQUIRED_FIELDS")
        return AgentOutput(12, self.agent_name, "COMPLETED", 0, 0.95,
            findings={"quality_score": score, "missing_fields": missing, "ocr_confidence": conf},
            flags=["LOW_QUALITY"] if score < 60 else [])

class Agent13Trend(BaseAgent):
    agent_id = 13; agent_name = "Trend Analyzer"; tier = AgentTier.MERCHANT
    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        vs_avg = round(random.uniform(-0.5,2.0),2)
        timing = "business_hours" if random.random()>0.2 else "unusual_hours"
        flags  = []
        if vs_avg > 1.5: flags.append("AMOUNT_50PCT_ABOVE_AVERAGE"); ctx.fraud_flags.append("UNUSUAL_AMOUNT_TREND")
        if timing == "unusual_hours": flags.append("OUTSIDE_BUSINESS_HOURS")
        return AgentOutput(13, self.agent_name, "COMPLETED", 0, 0.82,
            findings={"vendor_trend": random.choice(["increasing","stable","decreasing"]),
                      "amount_vs_avg": vs_avg, "submission_timing": timing,
                      "seasonal_expected": random.random()>0.3}, flags=flags)

# ── Tier 4 ────────────────────────────────────────────────
class Agent14Security(BaseAgent):
    agent_id = 14; agent_name = "Security Sentinel"; tier = AgentTier.SECURITY
    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        nfc = random.random() < 0.03; geo = random.random() < 0.05
        flags = []
        if nfc: flags.append("NFC_RELAY_DETECTED"); ctx.fraud_flags.append("NFC_RELAY_ATTACK")
        if geo: flags.append("GEO_VELOCITY_EXCEEDED"); ctx.fraud_flags.append("IMPOSSIBLE_TRAVEL")
        level = "CRITICAL" if len(flags)>=2 else "HIGH" if flags else "LOW"
        ctx.security_data.update({"nfc_relay_detected": nfc, "geo_velocity_exceeded": geo,
            "threat_level": level, "threat_details": flags})
        return AgentOutput(14, self.agent_name, "COMPLETED", 0, 0.91,
            findings={"nfc_relay": nfc, "geo_velocity": geo, "threat_level": level}, flags=flags)

class Agent15FraudRing(BaseAgent):
    agent_id = 15; agent_name = "Fraud Ring Analyzer"; tier = AgentTier.SECURITY
    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        ring = random.random() < 0.04; size = random.randint(3,12) if ring else 0
        attrs = random.sample(["shared_bank_account","same_ip_subnet","similar_invoice_pattern","common_beneficiary"],
                              k=random.randint(1,3)) if ring else []
        if ring: ctx.fraud_flags.append("FRAUD_RING_MEMBER"); ctx.security_data["fraud_ring_detected"] = True
        return AgentOutput(15, self.agent_name, "COMPLETED", 0, 0.93 if ring else 0.98,
            findings={"fraud_ring_detected": ring, "ring_size": size, "shared_attributes": attrs},
            flags=["FRAUD_RING"] if ring else [])

class Agent16Behavioral(BaseAgent):
    agent_id = 16; agent_name = "Behavioral Consistency"; tier = AgentTier.SECURITY
    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        anomaly = random.random() < 0.06
        if anomaly: ctx.fraud_flags.append("BEHAVIORAL_ANOMALY"); ctx.security_data["behavioral_inconsistency"] = True
        conf = round(random.uniform(0.85,0.99),3)
        return AgentOutput(16, self.agent_name, "COMPLETED", 0, conf,
            findings={"behavioral_anomaly": anomaly, "typing_pattern_match": not anomaly,
                      "device_fingerprint_match": not anomaly, "confidence": conf},
            flags=["BEHAVIORAL_ANOMALY"] if anomaly else [])
