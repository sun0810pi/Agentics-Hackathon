"""Agent 3: AI Analyst - AWS Bedrock Claude for risk scoring"""
from agents.base import BaseAgent
from services.aws_service import bedrock_service
from typing import Dict, Any, List, Tuple

class Agent3AIAnalyst(BaseAgent):
    agent_id = 3
    agent_name = "AI Analyst"
    tier = "Core Detection"

    async def _execute(self, invoice_data: Dict, context: Dict) -> Tuple[Dict, List[str], float]:
        ocr_fields = context.get("results", {}).get(0, {}).get("invoice_fields", {})
        analysis = bedrock_service.analyze_fraud_risk(ocr_fields)
        flags = analysis.get("flags", [])
        risk_score = analysis.get("risk_score", 50)
        if risk_score >= 70:
            flags.append("HIGH_AI_RISK_SCORE")
        return {
            "risk_score": risk_score,
            "decision": analysis.get("decision", "REVIEW"),
            "reasoning": analysis.get("reasoning", ""),
            "anomalies": analysis.get("anomalies", {}),
        }, flags, analysis.get("confidence", 0.7)
