"""
backend/agents/orchestrator.py
================================
Orchestrates all 17 agents and builds the final AnalyzeResponse.

Pipeline:
  Tier 1 (Core):        Agents 0-7  → sequential (each depends on prior)
  Tier 2 (Intelligence):Agents 8-10 → parallel
  Tier 3 (Merchant):    Agents 11-13→ parallel
  Tier 4 (Security):    Agents 14-16→ parallel

Tiers 2-4 run concurrently after Tier 1 completes.
"""

import asyncio
import time
import hashlib
import json
import logging
import uuid
from datetime import datetime
from typing import Optional

from agents.base import AgentContext
from agents.tier1_core.agents import (
    Agent0OCR, Agent1PII, Agent2Decimal, Agent3AIAnalyst,
    Agent4Audit, Agent5Notifier, Agent6Dashboard, Agent7Integrator,
)
from agents.all_agents import (
    Agent8MLInsights, Agent9Learning, Agent10Currency,
    Agent11Merchant, Agent12Quality, Agent13Trend,
    Agent14Security, Agent15FraudRing, Agent16Behavioral,
)

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Runs the 17-agent pipeline and returns a complete AnalyzeResponse dict.
    """

    def __init__(self):
        # Tier 1: Core Detection — order matters!
        self.tier1 = [
            Agent0OCR(),
            Agent1PII(),
            Agent2Decimal(),
            Agent3AIAnalyst(),
            Agent4Audit(),
            Agent5Notifier(),
            Agent6Dashboard(),
            Agent7Integrator(),
        ]
        # Tiers 2-4: run in parallel after Tier 1
        self.tier2 = [Agent8MLInsights(), Agent9Learning(),  Agent10Currency()]
        self.tier3 = [Agent11Merchant(),  Agent12Quality(),  Agent13Trend()]
        self.tier4 = [Agent14Security(),  Agent15FraudRing(), Agent16Behavioral()]

    async def run(
        self,
        invoice_id: str,
        file_name:  str,
        file_data:  bytes,
        mode:       str = "full",
        trace_id:   Optional[str] = None,
    ) -> dict:
        """
        Execute the full pipeline.
        Returns a dict matching shared/models.py → AnalyzeResponse.
        """
        started_at = datetime.utcnow()
        request_id = str(uuid.uuid4())
        if not trace_id:
            trace_id = f"1-{hex(int(time.time()))[2:]}-{uuid.uuid4().hex[:24]}"

        logger.info(f"Pipeline start: invoice={invoice_id} mode={mode} trace={trace_id[:16]}...")

        # Build shared context
        ctx = AgentContext(
            invoice_id=invoice_id,
            file_name=file_name,
            file_data=file_data,
            mode=mode,
            trace_id=trace_id,
        )

        try:
            # ── Tier 1: Sequential ─────────────────────────────
            for agent in self.tier1:
                if mode == "fast" and agent.agent_id >= 5:
                    break  # fast mode: only agents 0-4
                await agent.run(ctx)

            # ── Tiers 2-4: Parallel ────────────────────────────
            if mode == "full":
                await asyncio.gather(
                    *[a.run(ctx) for a in self.tier2],
                    *[a.run(ctx) for a in self.tier3],
                    *[a.run(ctx) for a in self.tier4],
                    return_exceptions=True,
                )

        except Exception as e:
            logger.error(f"Pipeline error: {e}")

        completed_at   = datetime.utcnow()
        total_duration = (completed_at - started_at).total_seconds() * 1000

        # ── Build response ────────────────────────────────────
        response = self._build_response(
            ctx=ctx,
            invoice_id=invoice_id,
            trace_id=trace_id,
            request_id=request_id,
            started_at=started_at,
            completed_at=completed_at,
            total_duration=total_duration,
            mode=mode,
        )

        logger.info(
            f"Pipeline done: invoice={invoice_id} "
            f"decision={response['final_decision']} "
            f"risk={response['risk']['risk_score']} "
            f"duration={total_duration:.0f}ms"
        )
        return response

    def _build_response(
        self,
        ctx: AgentContext,
        invoice_id: str,
        trace_id: str,
        request_id: str,
        started_at: datetime,
        completed_at: datetime,
        total_duration: float,
        mode: str,
    ) -> dict:
        """Assemble the final response dict from context."""

        agents_run       = len(ctx.agent_results)
        agents_succeeded = sum(1 for r in ctx.agent_results if r["status"] == "COMPLETED")
        agents_failed    = sum(1 for r in ctx.agent_results if r["status"] == "FAILED")

        # Risk data from Agent 3
        risk = ctx.risk_data or {
            "risk_score": 0, "risk_level": "LOW",
            "decision": "APPROVE", "confidence": 0.5,
            "risk_factors": [], "explanation": "No analysis",
        }

        # Security data from Tier 4
        sec = ctx.security_data
        security = {
            "nfc_relay_detected":        sec.get("nfc_relay_detected", False),
            "geo_velocity_exceeded":     sec.get("geo_velocity_exceeded", False),
            "fraud_ring_detected":       sec.get("fraud_ring_detected", False),
            "behavioral_inconsistency":  sec.get("behavioral_inconsistency", False),
            "threat_level":              sec.get("threat_level", "LOW"),
            "threat_details":            sec.get("threat_details", []),
            "recommended_actions": (
                ["Block and investigate", "Notify security team"] if sec.get("threat_level") == "CRITICAL"
                else ["Monitor", "Flag for review"] if sec.get("threat_details")
                else []
            ),
        }

        # Fraud indicators
        flags = ctx.fraud_flags
        fraud_indicators = {
            "duplicate_invoice":    "DUPLICATE_INVOICE" in flags,
            "amount_mismatch":      any("MISMATCH" in f for f in flags),
            "suspicious_vendor":    "SUSPICIOUS_VENDOR" in flags,
            "unusual_timing":       "SUBMITTED_OUTSIDE_BUSINESS_HOURS" in flags,
            "geo_velocity_flag":    "IMPOSSIBLE_TRAVEL" in flags,
            "fraud_ring_member":    "FRAUD_RING_MEMBER" in flags,
            "behavioral_anomaly":   "BEHAVIORAL_ANOMALY" in flags,
            "total_flags":          len(flags),
            "flag_details":         flags,
        }

        # Build full response payload
        payload = {
            "invoice_id":        invoice_id,
            "trace_id":          trace_id,
            "request_id":        request_id,
            "started_at":        started_at.isoformat(),
            "completed_at":      completed_at.isoformat(),
            "total_duration_ms": round(total_duration, 2),
            "mode":              mode,
            "agents_run":        agents_run,
            "agents_succeeded":  agents_succeeded,
            "agents_failed":     agents_failed,
            "extracted":         ctx.extracted,
            "pii_report":        ctx.pii_report,
            "risk":              risk,
            "fraud_indicators":  fraud_indicators,
            "security":          security,
            "ml_insights":       ctx.ml_data or {},
            "final_decision":    risk.get("decision", "ERROR"),
            "final_confidence":  risk.get("confidence", 0.5),
            "agent_results":     ctx.agent_results,
        }

        # Immutable audit hash
        payload["audit_hash"] = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()

        return payload
