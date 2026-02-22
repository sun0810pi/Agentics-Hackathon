"""
tests/backend/test_agents.py
=============================
Unit tests cho agent pipeline.
Run: pytest tests/backend/test_agents.py -v
"""
import asyncio, pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from agents.base import AgentContext
from agents.tier1_core import Agent0OCR, Agent1PII, Agent2Decimal, Agent4Audit
from agents.agents_9_to_16 import Agent10Currency, Agent12Quality


def make_ctx(mode="demo") -> AgentContext:
    return AgentContext(invoice_id="INV-TEST-0001", file_name="test.pdf", file_data=b"", mode=mode)


@pytest.mark.asyncio
async def test_agent0_ocr_demo():
    ctx = make_ctx("demo")
    out = await Agent0OCR().run(ctx)
    assert out.status == "COMPLETED"
    assert out.confidence > 0.5
    assert ctx.extracted.get("total_amount") is not None
    assert ctx.extracted.get("invoice_number") is not None


@pytest.mark.asyncio
async def test_agent1_pii_no_pii():
    ctx = make_ctx("demo")
    ctx.extracted = {"vendor_name": "SafeVendor Corp", "invoice_number": "INV-2026-0001"}
    out = await Agent1PII().run(ctx)
    assert out.status == "COMPLETED"
    assert ctx.pii_report["gdpr_compliant"] is True


@pytest.mark.asyncio
async def test_agent2_decimal_valid():
    ctx = make_ctx("demo")
    ctx.extracted = {"subtotal": 100.0, "tax_amount": 10.0, "total_amount": 110.0,
                     "line_items": [{"amount": 100.0}]}
    out = await Agent2Decimal().run(ctx)
    assert out.status == "COMPLETED"
    assert out.findings.get("validated") is True
    assert len(out.flags) == 0


@pytest.mark.asyncio
async def test_agent2_decimal_mismatch():
    ctx = make_ctx("demo")
    ctx.extracted = {"subtotal": 100.0, "tax_amount": 10.0, "total_amount": 999.0,
                     "line_items": [{"amount": 100.0}]}
    out = await Agent2Decimal().run(ctx)
    assert "TOTAL_AMOUNT_MISMATCH" in out.flags
    assert out.findings.get("validated") is False


@pytest.mark.asyncio
async def test_agent4_audit_creates_hash():
    ctx = make_ctx("demo")
    ctx.extracted  = {"total_amount": 1000.0}
    ctx.risk_data  = {"risk_score": 25, "decision": "APPROVE"}
    out = await Agent4Audit().run(ctx)
    assert out.status == "COMPLETED"
    h = out.findings.get("audit_hash", "")
    assert len(h) == 64                  # SHA-256 hex


@pytest.mark.asyncio
async def test_agent10_currency_usd():
    ctx = make_ctx("demo")
    ctx.extracted = {"currency": "USD", "total_amount": 5000.0}
    out = await Agent10Currency().run(ctx)
    assert out.findings["usd_equivalent"] == 5000.0


@pytest.mark.asyncio
async def test_agent12_quality_missing_fields():
    ctx = make_ctx("demo")
    ctx.extracted = {"ocr_confidence": 0.9}   # missing required fields
    out = await Agent12Quality().run(ctx)
    assert len(out.findings["missing_fields"]) > 0
    assert "MISSING_REQUIRED_FIELDS" in ctx.fraud_flags


@pytest.mark.asyncio
async def test_full_pipeline_demo():
    """End-to-end demo pipeline."""
    from agents.orchestrator import AgentOrchestrator
    orch   = AgentOrchestrator()
    result = await orch.run("INV-E2E-001", "invoice.pdf", b"", mode="demo")
    assert result["final_decision"] in ("APPROVE","REVIEW","BLOCK")
    assert result["final_confidence"] > 0
    assert result["agents_run"] > 0
    assert len(result["audit_hash"]) == 64
    assert result["extracted"].get("total_amount") is not None
