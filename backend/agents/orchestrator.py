"""
backend/agents/orchestrator.py
================================
Chạy 17 agents theo pipeline:
  Tier 1 (0-7): Sequential — mỗi agent phụ thuộc kết quả trước
  Tier 2-4:     Parallel   — asyncio.gather, return_exceptions=True
"""

import asyncio, time, hashlib, json, logging, uuid
from datetime import datetime
from typing import Optional
from agents.base import AgentContext
from agents.tier1_core    import Agent0OCR, Agent1PII, Agent2Decimal, Agent3AIAnalyst, Agent4Audit, Agent5Notifier, Agent6Dashboard, Agent7Integrator
from agents.tier2_intelligence import Agent8MLInsights, Agent9Learning, Agent10Currency
from agents.tier3_merchant     import Agent11Merchant, Agent12Quality, Agent13Trend
from agents.tier4_security     import Agent14Security, Agent15FraudRing, Agent16Behavioral

logger = logging.getLogger(__name__)


class AgentOrchestrator:

    def __init__(self):
        self.tier1 = [Agent0OCR(), Agent1PII(), Agent2Decimal(), Agent3AIAnalyst(),
                      Agent4Audit(), Agent5Notifier(), Agent6Dashboard(), Agent7Integrator()]
        self.tier2 = [Agent8MLInsights(), Agent9Learning(), Agent10Currency()]
        self.tier3 = [Agent11Merchant(), Agent12Quality(), Agent13Trend()]
        self.tier4 = [Agent14Security(), Agent15FraudRing(), Agent16Behavioral()]

    async def run(self, invoice_id: str, file_name: str, file_data: bytes,
                  mode: str = "full", trace_id: Optional[str] = None) -> dict:

        started_at = datetime.utcnow()
        request_id = str(uuid.uuid4())
        trace_id   = trace_id or f"1-{hex(int(time.time()))[2:]}-{uuid.uuid4().hex[:24]}"

        logger.info(f"Pipeline START invoice={invoice_id} mode={mode}")

        ctx = AgentContext(invoice_id=invoice_id, file_name=file_name,
                           file_data=file_data, mode=mode, trace_id=trace_id)

        # ── Tier 1: Sequential ─────────────────────────────────────
        for agent in self.tier1:
            if mode == "fast" and agent.agent_id >= 5:
                break
            await agent.run(ctx)

        # ── Tiers 2-4: Parallel ────────────────────────────────────
        if mode == "full":
            await asyncio.gather(
                *[a.run(ctx) for a in self.tier2],
                *[a.run(ctx) for a in self.tier3],
                *[a.run(ctx) for a in self.tier4],
                return_exceptions=True,   # ← một agent crash không kill cả pipeline
            )

        completed_at   = datetime.utcnow()
        total_ms       = (completed_at - started_at).total_seconds() * 1000

        response = self._build(ctx, invoice_id, trace_id, request_id, started_at, completed_at, total_ms, mode)
        logger.info(f"Pipeline DONE invoice={invoice_id} decision={response['final_decision']} {total_ms:.0f}ms")
        return response

    def _build(self, ctx, invoice_id, trace_id, request_id, started_at, completed_at, total_ms, mode) -> dict:
        results   = ctx.agent_results
        succeeded = sum(1 for r in results if r["status"] == "COMPLETED")
        failed    = sum(1 for r in results if r["status"] == "FAILED")
        risk      = ctx.risk_data or {"risk_score":0,"risk_level":"LOW","decision":"APPROVE","confidence":0.5,"risk_factors":[],"explanation":""}
        sec       = ctx.security_data
        flags     = ctx.fraud_flags

        payload = {
            "invoice_id":        invoice_id,
            "trace_id":          trace_id,
            "request_id":        request_id,
            "started_at":        started_at.isoformat(),
            "completed_at":      completed_at.isoformat(),
            "total_duration_ms": round(total_ms, 2),
            "mode":              mode,
            "agents_run":        len(results),
            "agents_succeeded":  succeeded,
            "agents_failed":     failed,
            "extracted":         ctx.extracted,
            "pii_report":        ctx.pii_report,
            "risk":              risk,
            "fraud_indicators": {
                "duplicate_invoice":   "DUPLICATE_INVOICE" in flags,
                "amount_mismatch":     any("MISMATCH" in f for f in flags),
                "suspicious_vendor":   "SUSPICIOUS_VENDOR" in flags,
                "unusual_timing":      "OUTSIDE_BUSINESS_HOURS" in flags,
                "geo_velocity_flag":   "IMPOSSIBLE_TRAVEL" in flags,
                "fraud_ring_member":   "FRAUD_RING_MEMBER" in flags,
                "behavioral_anomaly":  "BEHAVIORAL_ANOMALY" in flags,
                "total_flags":         len(flags),
                "flag_details":        flags,
            },
            "security": {
                "nfc_relay_detected":       sec.get("nfc_relay_detected", False),
                "geo_velocity_exceeded":    sec.get("geo_velocity_exceeded", False),
                "fraud_ring_detected":      sec.get("fraud_ring_detected", False),
                "behavioral_inconsistency": sec.get("behavioral_inconsistency", False),
                "threat_level":             sec.get("threat_level", "LOW"),
                "threat_details":           sec.get("threat_details", []),
                "recommended_actions":      ["Block and investigate","Notify security team"] if sec.get("threat_level") == "CRITICAL" else [],
            },
            "ml_insights":      ctx.ml_data or {},
            "final_decision":   risk.get("decision", "ERROR"),
            "final_confidence": risk.get("confidence", 0.5),
            "agent_results":    results,
        }
        payload["audit_hash"] = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()
        return payload
