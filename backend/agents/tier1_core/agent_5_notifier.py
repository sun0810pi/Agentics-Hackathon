"""Agent 5: Notifier - Sends alerts for high-risk invoices"""
import logging
from agents.base import BaseAgent
from typing import Dict, Any, List, Tuple
logger = logging.getLogger(__name__)

class Agent5Notifier(BaseAgent):
    agent_id = 5
    agent_name = "Notifier"
    tier = "Core Detection"

    async def _execute(self, invoice_data: Dict, context: Dict) -> Tuple[Dict, List[str], float]:
        ai_result = context.get("results", {}).get(3, {})
        risk_score = ai_result.get("risk_score", 0)
        notifications_sent = []

        if risk_score >= 70:
            # In production: call Slack/SNS/SES APIs here
            notifications_sent.append("SLACK_ALERT")
            notifications_sent.append("EMAIL_ALERT")
            logger.info(f"High-risk alert sent for invoice {context.get('invoice_id')}")

        return {
            "notifications_sent": notifications_sent,
            "risk_threshold_triggered": risk_score >= 70,
        }, [], 0.9
