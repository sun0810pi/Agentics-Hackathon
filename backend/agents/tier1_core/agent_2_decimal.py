"""backend/agents/tier1_core/agent_2_decimal.py — Amount Validator"""
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier

class Agent2Decimal(BaseAgent):
    agent_id = 2; agent_name = "Decimal Matcher"; tier = AgentTier.CORE
    TOLERANCE = 0.02

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        e = ctx.extracted
        flags, findings = [], {}
        line_total = sum(float(i.get("amount", 0)) for i in e.get("line_items", []))
        subtotal   = float(e.get("subtotal", 0))
        tax        = float(e.get("tax_amount", 0))
        total      = float(e.get("total_amount", 0))

        if abs(line_total - subtotal) > self.TOLERANCE and line_total > 0:
            flags.append("LINE_ITEMS_SUM_MISMATCH"); findings["line_delta"] = round(line_total - subtotal, 2)
        if abs((subtotal + tax) - total) > self.TOLERANCE and subtotal > 0:
            flags.append("TOTAL_AMOUNT_MISMATCH"); findings["total_delta"] = round((subtotal+tax)-total, 2)
        if total <= 0:   flags.append("ZERO_OR_NEGATIVE_AMOUNT")
        if total > 1e6:  flags.append("UNUSUALLY_LARGE_AMOUNT")
        if total > 0 and (tax/total)*100 > 30: flags.append("ABNORMAL_TAX_RATE")

        ctx.fraud_flags.extend(flags)
        findings["validated"] = len(flags) == 0
        conf = max(0.3, 0.95 - len(flags) * 0.2)
        return AgentOutput(2, self.agent_name, "COMPLETED", 0, conf, findings=findings, flags=flags)
