"""
backend/agents/base.py
=======================
Base class cho tất cả 17 agents.

PERF FIXES:
  - logger.info → logger.debug per-agent (giảm 34 log lines/invoice xuống 0)
  - X-Ray import moved to module level (17× per pipeline → 1×)
  - X-Ray availability cached as class var (không re-try import mỗi call)
"""

import time, logging, abc
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# ── X-Ray: import once at module level, cache availability ─
try:
    from services.xray_tracer import xray_subsegment as _xray_sub
    _XRAY_OK = True
except Exception:
    _XRAY_OK = False
    _xray_sub = None


class AgentTier(str, Enum):
    CORE         = "tier1_core"
    INTELLIGENCE = "tier2_intelligence"
    MERCHANT     = "tier3_merchant"
    SECURITY     = "tier4_security"


@dataclass
class AgentContext:
    """Shared context được pass qua tất cả agents."""
    invoice_id:   str
    file_name:    str
    file_data:    bytes
    mode:         str  = "full"
    trace_id:     str  = ""

    extracted:     Dict[str, Any] = field(default_factory=dict)
    pii_report:    Dict[str, Any] = field(default_factory=dict)
    risk_data:     Dict[str, Any] = field(default_factory=dict)
    fraud_flags:   List[str]      = field(default_factory=list)
    security_data: Dict[str, Any] = field(default_factory=dict)
    ml_data:       Dict[str, Any] = field(default_factory=dict)
    audit_entries: List[str]      = field(default_factory=list)

    started_at:    float               = field(default_factory=time.time)
    agent_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentOutput:
    """Kết quả từ một agent."""
    agent_id:    int
    agent_name:  str
    status:      str          # COMPLETED | FAILED | SKIPPED
    duration_ms: float
    confidence:  float
    findings:    Dict[str, Any] = field(default_factory=dict)
    flags:       List[str]      = field(default_factory=list)
    error:       Optional[str]  = None


class BaseAgent(abc.ABC):
    """
    Abstract base class. Override _execute(), không override run().
    """
    agent_id:   int
    agent_name: str
    tier:       AgentTier
    enabled:    bool = True

    async def run(self, context: AgentContext) -> AgentOutput:
        if not self.enabled:
            return AgentOutput(
                agent_id=self.agent_id, agent_name=self.agent_name,
                status="SKIPPED", duration_ms=0.0, confidence=0.0,
            )

        start = time.perf_counter()
        # PERF: debug-only log — no INFO spam per agent
        logger.debug(f"[Agent {self.agent_id}] {self.agent_name} START")

        try:
            # PERF: X-Ray availability cached at import time (no per-call try/except)
            if _XRAY_OK and _xray_sub:
                with _xray_sub(f"agent_{self.agent_id}_{self.agent_name}"):
                    output = await self._execute(context)
            else:
                output = await self._execute(context)

        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(f"[Agent {self.agent_id}] {self.agent_name} FAILED: {e}")
            output = AgentOutput(
                agent_id=self.agent_id, agent_name=self.agent_name,
                status="FAILED", duration_ms=round(duration_ms, 2),
                confidence=0.0, error=str(e),
            )

        output.duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.debug(
            f"[Agent {self.agent_id}] {self.agent_name} "
            f"{output.status} {output.duration_ms:.1f}ms"
        )

        context.agent_results.append({
            "agent_id":    output.agent_id,
            "agent_name":  output.agent_name,
            "status":      output.status,
            "duration_ms": output.duration_ms,
            "confidence":  output.confidence,
            "findings":    output.findings,
            "flags":       output.flags,
            "error":       output.error,
        })
        return output

    @abc.abstractmethod
    async def _execute(self, context: AgentContext) -> AgentOutput: ...

    def _demo_mode(self, ctx: AgentContext) -> bool:
        return ctx.mode == "demo"
