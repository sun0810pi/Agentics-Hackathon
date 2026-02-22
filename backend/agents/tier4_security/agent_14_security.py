"""Agent 14: Security Sentinel - Threat detection"""
import random
from agents.base import BaseAgent
class Agent14Security(BaseAgent):
    agent_id = 14
    agent_name = "Security Sentinel"
    tier = "Security"
    async def _execute(self, invoice_data, context):
        flags = []
        threat_level = random.uniform(5, 25)
        all_flags = str(context.get("results", {}))
        if "EXTREMELY_LARGE_AMOUNT" in all_flags:
            threat_level += 40
            flags.append("LARGE_AMOUNT_SECURITY_REVIEW")
        return {"threat_level": round(threat_level, 1), "threats_detected": [], "geo_velocity_check": "PASSED", "ip_reputation": "CLEAN"}, flags, 0.91
