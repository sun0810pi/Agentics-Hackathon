"""backend/agents/tier1_core/agent_4_audit.py — Immutable Audit Trail"""
import hashlib, json, time, logging
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier
logger = logging.getLogger(__name__)

class Agent4Audit(BaseAgent):
    agent_id = 4; agent_name = "Audit Seal"; tier = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        payload = json.dumps({"invoice_id": ctx.invoice_id, "extracted": ctx.extracted,
            "risk_score": ctx.risk_data.get("risk_score", 0), "decision": ctx.risk_data.get("decision", "ERROR"),
            "flags": ctx.fraud_flags, "timestamp": time.time(), "trace_id": ctx.trace_id}, sort_keys=True)
        h = hashlib.sha256(payload.encode()).hexdigest()
        entry = f"[{ctx.invoice_id}] decision={ctx.risk_data.get('decision','?')} hash={h[:16]}..."
        ctx.audit_entries.append(entry)
        return AgentOutput(4, self.agent_name, "COMPLETED", 0, 1.0, findings={"audit_hash": h, "entry": entry})


"""backend/agents/tier1_core/agent_5_notifier.py — Alert Notifications"""
import os, logging
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier
logger = logging.getLogger(__name__)

class Agent5Notifier(BaseAgent):
    agent_id = 5; agent_name = "Notifier"; tier = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        decision = ctx.risk_data.get("decision", "APPROVE")
        if decision not in ("BLOCK", "REVIEW"):
            return AgentOutput(5, self.agent_name, "SKIPPED", 0, 1.0, findings={"reason": f"{decision} — no alert needed"})
        if self._demo_mode(ctx):
            return AgentOutput(5, self.agent_name, "COMPLETED", 0, 1.0, findings={"sent": ["email(demo)", "slack(demo)"], "decision": decision})
        sent = []
        try:
            import boto3
            arn = os.getenv("SNS_ALERT_TOPIC_ARN")
            if arn:
                boto3.client("sns", region_name=os.getenv("AWS_REGION","us-east-1")).publish(
                    TopicArn=arn, Subject=f"AgentFlow {decision}: {ctx.invoice_id}",
                    Message=f"⚠️ {decision}: Invoice {ctx.invoice_id} | Risk={ctx.risk_data.get('risk_score')}")
                sent.append("sns")
        except Exception as e:
            logger.warning(f"SNS failed: {e}")
        return AgentOutput(5, self.agent_name, "COMPLETED", 0, 1.0, findings={"sent": sent, "decision": decision})


"""backend/agents/tier1_core/agent_6_dashboard.py — Dashboard Aggregator"""
import time
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier

class Agent6Dashboard(BaseAgent):
    agent_id = 6; agent_name = "Dashboard Data"; tier = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        summary = {"invoice_id": ctx.invoice_id, "vendor": ctx.extracted.get("vendor_name"),
            "amount": ctx.extracted.get("total_amount"), "currency": ctx.extracted.get("currency","USD"),
            "decision": ctx.risk_data.get("decision"), "risk_score": ctx.risk_data.get("risk_score"),
            "flags_count": len(ctx.fraud_flags), "processing_ms": round((time.time()-ctx.started_at)*1000,2)}
        return AgentOutput(6, self.agent_name, "COMPLETED", 0, 1.0, findings=summary)


"""backend/agents/tier1_core/agent_7_integrator.py — External Integrations"""
import os, logging
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier
logger = logging.getLogger(__name__)

class Agent7Integrator(BaseAgent):
    agent_id = 7; agent_name = "Integrator"; tier = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        if self._demo_mode(ctx):
            return AgentOutput(7, self.agent_name, "COMPLETED", 0, 1.0, findings={"synced_to": ["Google Sheets(demo)", "ERP(demo)"]})
        synced = []
        webhook = os.getenv("INTEGRATION_WEBHOOK_URL")
        if webhook:
            try:
                import httpx
                async with httpx.AsyncClient() as c:
                    await c.post(webhook, json={"invoice_id": ctx.invoice_id, "decision": ctx.risk_data.get("decision"), "risk_score": ctx.risk_data.get("risk_score")}, timeout=5.0)
                synced.append("webhook")
            except Exception as e:
                logger.warning(f"Webhook failed: {e}")
        return AgentOutput(7, self.agent_name, "COMPLETED", 0, 1.0, findings={"synced_to": synced})
