"""backend/agents/tier1_core/agent_1_pii.py — PII Preprocessor"""
import re, logging
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier
logger = logging.getLogger(__name__)

class Agent1PII(BaseAgent):
    agent_id = 1; agent_name = "PII Preprocessor"; tier = AgentTier.CORE
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(\+\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}\b',
        "ssn":   r'\b\d{3}-\d{2}-\d{4}\b',
        "cc":    r'\b(?:\d[ -]?){13,16}\b',
    }

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        masked_fields, masked_data = [], {}
        for field_name, value in {"vendor_name": ctx.extracted.get("vendor_name",""), "invoice_number": ctx.extracted.get("invoice_number","")}.items():
            original, masked = str(value), str(value)
            for pii_type, pattern in self.PATTERNS.items():
                if re.search(pattern, original):
                    masked = re.sub(pattern, f"[{pii_type.upper()}_MASKED]", masked)
                    masked_fields.append(f"{field_name}:{pii_type}")
            if masked != original:
                masked_data[field_name] = masked
        pii = len(masked_fields) > 0
        ctx.pii_report = {"fields_masked": masked_fields, "gdpr_compliant": True, "pii_detected": pii, "masked_data": masked_data}
        return AgentOutput(1, self.agent_name, "COMPLETED", 0, 0.99, findings=ctx.pii_report, flags=["PII_DETECTED"] if pii else [])
