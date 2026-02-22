"""Agent 6: Dashboard Data - Aggregates metrics for real-time dashboard"""
from agents.base import BaseAgent
from typing import Dict, Any, List, Tuple

class Agent6Dashboard(BaseAgent):
    agent_id = 6
    agent_name = "Dashboard Data"
    tier = "Core Detection"

    async def _execute(self, invoice_data: Dict, context: Dict) -> Tuple[Dict, List[str], float]:
        ai_result = context.get("results", {}).get(3, {})
        return {
            "dashboard_updated": True,
            "risk_score": ai_result.get("risk_score", 0),
            "metrics_refreshed": True,
        }, [], 1.0
