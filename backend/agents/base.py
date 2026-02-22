"""
backend/agents/base.py
=======================
Base class cho tất cả 17 agents.
Mọi agent đều kế thừa class này và implement _execute().
"""

import time
import logging
import abc
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AgentTier(str, Enum):
    CORE         = "tier1_core"
    INTELLIGENCE = "tier2_intelligence"
    MERCHANT     = "tier3_merchant"
    SECURITY     = "tier4_security"


@dataclass
class AgentContext:
    """
    Shared context được pass qua tất cả agents.
    Agents đọc từ context và ghi kết quả vào context.
    """
    invoice_id:   str
    file_name:    str
    file_data:    bytes
    mode:         str = "full"   # full | fast | demo
    trace_id:     str = ""

    # Populated by agents as they run
    extracted:     Dict[str, Any] = field(default_factory=dict)
    pii_report:    Dict[str, Any] = field(default_factory=dict)
    risk_data:     Dict[str, Any] = field(default_factory=dict)
    fraud_flags:   List[str]      = field(default_factory=list)
    security_data: Dict[str, Any] = field(default_factory=dict)
    ml_data:       Dict[str, Any] = field(default_factory=dict)
    audit_entries: List[str]      = field(default_factory=list)

    started_at:    float = field(default_factory=time.time)
    agent_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentOutput:
    """Kết quả từ một agent."""
    agent_id:    int
    agent_name:  str
    status:      str          # COMPLETED | FAILED | SKIPPED
    duration_ms: float
    confidence:  float        # 0.0 - 1.0
    findings:    Dict[str, Any] = field(default_factory=dict)
    flags:       List[str]      = field(default_factory=list)
    error:       Optional[str]  = None


class BaseAgent(abc.ABC):
    """
    Abstract base class cho tất cả agents.
    Override _execute(), không override run().
    """

    agent_id:   int
    agent_name: str
    tier:       AgentTier
    enabled:    bool = True

    async def run(self, context: AgentContext) -> AgentOutput:
        """Entry point. Wrap _execute với timing + error handling."""
        if not self.enabled:
            return AgentOutput(
                agent_id=self.agent_id, agent_name=self.agent_name,
                status="SKIPPED", duration_ms=0.0, confidence=0.0,
            )

        start = time.time()
        logger.info(f"[Agent {self.agent_id}] {self.agent_name} — START")

        try:
            # Wrap với X-Ray subsegment nếu có
            try:
                from services.xray_tracer import xray_subsegment
                with xray_subsegment(f"agent_{self.agent_id}_{self.agent_name}"):
                    output = await self._execute(context)
            except ImportError:
                output = await self._execute(context)

        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"[Agent {self.agent_id}] {self.agent_name} — FAILED: {e}")
            output = AgentOutput(
                agent_id=self.agent_id, agent_name=self.agent_name,
                status="FAILED", duration_ms=round(duration, 2),
                confidence=0.0, error=str(e),
            )

        output.duration_ms = round((time.time() - start) * 1000, 2)

        logger.info(
            f"[Agent {self.agent_id}] {self.agent_name} — "
            f"{output.status} {output.duration_ms:.0f}ms conf={output.confidence:.2f}"
        )

        # Ghi vào context để orchestrator tổng hợp
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
    async def _execute(self, context: AgentContext) -> AgentOutput:
        """Implement agent logic ở đây."""
        ...

    def _demo_mode(self, ctx: AgentContext) -> bool:
        return ctx.mode == "demo"
