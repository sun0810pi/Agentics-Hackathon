"""
backend/agents/base.py
=======================
Base class for all 17 AgentFlow agents.

Every agent:
- Has a unique ID (0-16) and name
- Implements async `run(context)` method
- Gets X-Ray subsegment automatically
- Reports status, duration, confidence
- Can fail gracefully without killing the orchestrator
"""

import time
import logging
import abc
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AgentTier(str, Enum):
    CORE        = "tier1_core"
    INTELLIGENCE = "tier2_intelligence"
    MERCHANT    = "tier3_merchant"
    SECURITY    = "tier4_security"


@dataclass
class AgentContext:
    """
    Shared context passed to every agent.
    Agents read from context and write their results back.
    This is the shared memory of the pipeline.
    """
    # Input
    invoice_id:   str
    file_name:    str
    file_data:    bytes           # Raw file bytes
    mode:         str  = "full"  # full | fast | demo
    trace_id:     str  = ""

    # Built up as agents run
    extracted:     Dict[str, Any] = field(default_factory=dict)
    pii_report:    Dict[str, Any] = field(default_factory=dict)
    risk_data:     Dict[str, Any] = field(default_factory=dict)
    fraud_flags:   List[str]      = field(default_factory=list)
    security_data: Dict[str, Any] = field(default_factory=dict)
    ml_data:       Dict[str, Any] = field(default_factory=dict)
    audit_entries: List[str]      = field(default_factory=list)

    # Metadata
    started_at: float = field(default_factory=time.time)
    agent_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentOutput:
    """Structured output from a single agent."""
    agent_id:   int
    agent_name: str
    status:     str         # COMPLETED | FAILED | SKIPPED
    duration_ms: float
    confidence: float       # 0.0 - 1.0
    findings:   Dict[str, Any] = field(default_factory=dict)
    flags:      List[str]      = field(default_factory=list)
    error:      Optional[str]  = None


class BaseAgent(abc.ABC):
    """
    Abstract base class for all 17 agents.

    Subclass this and implement `_execute(context)`.
    The base class handles:
    - Timing
    - X-Ray tracing
    - Error catching
    - Status reporting
    - Logging
    """

    agent_id:   int
    agent_name: str
    tier:       AgentTier
    enabled:    bool = True

    async def run(self, context: AgentContext) -> AgentOutput:
        """
        Public entry point. Wraps _execute with timing, tracing, error handling.
        Override _execute, not this.
        """
        if not self.enabled:
            return AgentOutput(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status="SKIPPED",
                duration_ms=0.0,
                confidence=0.0,
            )

        start = time.time()
        logger.info(f"[Agent {self.agent_id}] {self.agent_name} starting")

        try:
            from services.xray_tracer import xray_subsegment
            with xray_subsegment(f"agent_{self.agent_id}_{self.agent_name.lower().replace(' ', '_')}"):
                output = await self._execute(context)
        except ImportError:
            # X-Ray not available
            output = await self._execute(context)
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"[Agent {self.agent_id}] {self.agent_name} FAILED: {e}")
            output = AgentOutput(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status="FAILED",
                duration_ms=round(duration, 2),
                confidence=0.0,
                error=str(e),
            )

        output.duration_ms = round((time.time() - start) * 1000, 2)
        logger.info(
            f"[Agent {self.agent_id}] {self.agent_name} → "
            f"{output.status} in {output.duration_ms:.0f}ms "
            f"(conf={output.confidence:.2f})"
        )
        # Record in context
        context.agent_results.append({
            "agent_id":   output.agent_id,
            "agent_name": output.agent_name,
            "status":     output.status,
            "duration_ms": output.duration_ms,
            "confidence": output.confidence,
            "findings":   output.findings,
            "flags":      output.flags,
            "error":      output.error,
        })
        return output

    @abc.abstractmethod
    async def _execute(self, context: AgentContext) -> AgentOutput:
        """
        Implement the actual agent logic here.
        context.extracted, context.pii_report, etc. may be read/written.
        """
        ...

    def _demo_mode(self, context: AgentContext) -> bool:
        return context.mode == "demo"
