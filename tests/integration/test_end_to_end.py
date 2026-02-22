"""tests/integration/test_end_to_end.py — E2E pipeline test"""
import sys, os, pytest, asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

@pytest.mark.asyncio
async def test_full_pipeline_all_modes():
    from agents.orchestrator import AgentOrchestrator
    orch = AgentOrchestrator()
    for mode in ("demo", "fast"):
        result = await orch.run(f"INV-E2E-{mode.upper()}", "test.pdf", b"", mode=mode)
        assert result["final_decision"] in ("APPROVE","REVIEW","BLOCK"), f"Bad decision in {mode}"
        assert result["audit_hash"],   f"Missing audit hash in {mode}"
        assert result["agents_run"] > 0, f"No agents ran in {mode}"
        assert "extracted" in result,  f"Missing extracted in {mode}"
        assert "risk" in result,       f"Missing risk in {mode}"

@pytest.mark.asyncio
async def test_pipeline_handles_agent_failure():
    """Pipeline should complete even if individual agents fail."""
    from agents.orchestrator import AgentOrchestrator
    orch = AgentOrchestrator()
    # Pass empty bytes — some agents may warn but pipeline must complete
    result = await orch.run("INV-FAIL-TEST", "broken.pdf", b"", mode="demo")
    assert result is not None
    assert "final_decision" in result
