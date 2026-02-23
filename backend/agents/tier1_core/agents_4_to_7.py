"""
backend/agents/tier1_core/agents_4_to_7.py
Agents 4-7: Audit, Notifier, Dashboard, Integrator

PERF FIX:
  - Agent 5 SNS: sync boto3.publish() wrapped in run_in_executor
    (blocking call no longer stalls the event loop ~100-500ms)
  - SNS client cached as class attribute
"""
import hashlib, json, time, logging, os, asyncio
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier

logger = logging.getLogger(__name__)


# ── Agent 4 — Immutable Audit Trail ──────────────────────
class Agent4Audit(BaseAgent):
    agent_id = 4; agent_name = "Audit Seal"; tier = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        payload = json.dumps({
            "invoice_id": ctx.invoice_id,
            "extracted":  ctx.extracted,
            "risk_score": ctx.risk_data.get("risk_score", 0),
            "decision":   ctx.risk_data.get("decision", "ERROR"),
            "flags":      ctx.fraud_flags,
            "timestamp":  time.time(),
            "trace_id":   ctx.trace_id,
        }, sort_keys=True, default=str)
        audit_hash = hashlib.sha256(payload.encode()).hexdigest()
        entry = (
            f"[{ctx.invoice_id}] "
            f"decision={ctx.risk_data.get('decision', '?')} "
            f"risk={ctx.risk_data.get('risk_score', 0)} "
            f"hash={audit_hash[:16]}..."
        )
        ctx.audit_entries.append(entry)
        return AgentOutput(
            agent_id=4, agent_name=self.agent_name,
            status="COMPLETED", duration_ms=0, confidence=1.0,
            findings={"audit_hash": audit_hash, "entry": entry,
                      "flags_sealed": ctx.fraud_flags.copy()},
        )


# ── Agent 5 — Alert Notifications ────────────────────────
class Agent5Notifier(BaseAgent):
    agent_id = 5; agent_name = "Notifier"; tier = AgentTier.CORE

    # PERF: SNS client cached — not re-created every request
    _sns_client = None

    def _get_sns(self):
        if self._sns_client is None:
            try:
                import boto3
                Agent5Notifier._sns_client = boto3.client(
                    "sns", region_name=os.getenv("AWS_REGION", "us-east-1")
                )
            except Exception:
                pass
        return self._sns_client

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        decision = ctx.risk_data.get("decision", "APPROVE")

        if decision not in ("BLOCK", "REVIEW"):
            return AgentOutput(5, self.agent_name, "SKIPPED", 0, 1.0,
                               findings={"reason": f"{decision} — no alert needed"})

        if self._demo_mode(ctx):
            return AgentOutput(5, self.agent_name, "COMPLETED", 0, 1.0,
                               findings={"sent": ["email(demo)", "slack(demo)"], "decision": decision})

        sent = await self._send_alerts(ctx, decision)
        return AgentOutput(5, self.agent_name, "COMPLETED", 0, 1.0,
                           findings={"sent": sent, "decision": decision, "invoice_id": ctx.invoice_id})

    async def _send_alerts(self, ctx: AgentContext, decision: str) -> list:
        arn = os.getenv("SNS_ALERT_TOPIC_ARN", "")
        if not arn:
            logger.warning("SNS_ALERT_TOPIC_ARN not set — no alerts sent")
            return []

        sns = self._get_sns()
        if sns is None:
            return []

        risk  = ctx.risk_data.get("risk_score", 0)
        emoji = "🚨" if decision == "BLOCK" else "⚠️"
        msg   = (
            f"{emoji} {decision} detected\n"
            f"Invoice: {ctx.invoice_id}\n"
            f"Risk Score: {risk}/100\n"
            f"Flags: {', '.join(ctx.fraud_flags) or 'none'}\n"
            f"Trace: {ctx.trace_id}"
        )
        attrs = {
            "decision":   {"DataType": "String", "StringValue": decision},
            "risk_score": {"DataType": "Number", "StringValue": str(risk)},
        }

        # PERF FIX: sns.publish() is synchronous/blocking — run in executor
        # to avoid blocking the event loop for ~100-500ms
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,   # default ThreadPoolExecutor
                lambda: sns.publish(
                    TopicArn=arn,
                    Subject=f"AgentFlow {decision}: {ctx.invoice_id}",
                    Message=msg,
                    MessageAttributes=attrs,
                )
            )
            return ["sns"]
        except Exception as e:
            logger.warning(f"SNS publish failed: {e}")
            return []


# ── Agent 6 — Dashboard Aggregator ───────────────────────
class Agent6Dashboard(BaseAgent):
    agent_id = 6; agent_name = "Dashboard Data"; tier = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        elapsed_ms = round((time.time() - ctx.started_at) * 1000, 2)
        summary = {
            "invoice_id":     ctx.invoice_id,
            "vendor":         ctx.extracted.get("vendor_name", "Unknown"),
            "amount":         ctx.extracted.get("total_amount", 0),
            "currency":       ctx.extracted.get("currency", "USD"),
            "decision":       ctx.risk_data.get("decision", "ERROR"),
            "risk_score":     ctx.risk_data.get("risk_score", 0),
            "risk_level":     ctx.risk_data.get("risk_level", "UNKNOWN"),
            "flags_count":    len(ctx.fraud_flags),
            "flags":          ctx.fraud_flags.copy(),
            "processing_ms":  elapsed_ms,
            "ocr_confidence": ctx.extracted.get("ocr_confidence", 0),
        }
        return AgentOutput(6, self.agent_name, "COMPLETED", 0, 1.0, findings=summary)


# ── Agent 7 — External Integrations ──────────────────────
class Agent7Integrator(BaseAgent):
    agent_id = 7; agent_name = "Integrator"; tier = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        if self._demo_mode(ctx):
            return AgentOutput(7, self.agent_name, "COMPLETED", 0, 1.0,
                               findings={"synced_to": ["Google Sheets (demo)", "ERP (demo)"]})
        synced = await self._sync_external(ctx)
        return AgentOutput(7, self.agent_name, "COMPLETED", 0, 1.0,
                           findings={"synced_to": synced, "invoice_id": ctx.invoice_id})

    async def _sync_external(self, ctx: AgentContext) -> list:
        webhook = os.getenv("INTEGRATION_WEBHOOK_URL", "")
        if not webhook:
            return []
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as c:
                resp = await c.post(webhook, json={
                    "invoice_id": ctx.invoice_id,
                    "decision":   ctx.risk_data.get("decision"),
                    "risk_score": ctx.risk_data.get("risk_score"),
                    "timestamp":  time.time(),
                })
                resp.raise_for_status()
            return ["webhook"]
        except Exception as e:
            logger.warning(f"Webhook sync failed: {e}")
            return []
