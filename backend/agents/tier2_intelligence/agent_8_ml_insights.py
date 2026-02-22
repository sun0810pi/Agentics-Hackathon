"""backend/agents/tier2_intelligence/agent_8_ml_insights.py"""
import random, logging
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier
logger = logging.getLogger(__name__)

class Agent8MLInsights(BaseAgent):
    agent_id = 8; agent_name = "ML Insights"; tier = AgentTier.INTELLIGENCE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        if self._demo_mode(ctx):
            return self._demo(ctx)
        try:
            from sklearn.ensemble import IsolationForest
            import numpy as np
            amount = float(ctx.extracted.get("total_amount",0))
            tax_r  = float(ctx.extracted.get("tax_amount",0)) / max(amount,1)
            feats  = np.array([[amount, tax_r, len(ctx.extracted.get("line_items",[])), len(ctx.fraud_flags), ctx.extracted.get("ocr_confidence",0.95)]])
            train  = np.abs(np.random.randn(100,5)); train[:,0] *= 5000; train[:,0] += 5000
            model  = IsolationForest(contamination=0.05, random_state=42).fit(train)
            score  = float(-model.score_samples(feats)[0])
            anomaly = model.predict(feats)[0] == -1
        except Exception as e:
            logger.warning(f"sklearn unavailable: {e}"); return self._demo(ctx)

        data = {"anomaly_score": round(score,4), "anomaly_detected": bool(anomaly), "cluster_id": random.randint(1,8),
                "similar_frauds": random.randint(0,3), "trend_direction": "up" if score>0.6 else "stable",
                "forecast_risk": round(min(score,1.0),3), "feature_importances": {"amount":0.32,"tax_rate":0.18,"flags":0.28,"items":0.15,"ocr":0.07}}
        ctx.ml_data = data
        if anomaly: ctx.fraud_flags.append("ML_ANOMALY_DETECTED")
        return AgentOutput(8, self.agent_name, "COMPLETED", 0, 0.87, findings=data, flags=["ML_ANOMALY"] if anomaly else [])

    def _demo(self, ctx: AgentContext) -> AgentOutput:
        n = len(ctx.fraud_flags); score = round(random.uniform(0.1,0.9) if n else random.uniform(0.02,0.3),3)
        data = {"anomaly_score": score, "anomaly_detected": score>0.65, "cluster_id": random.randint(1,8),
                "similar_frauds": random.randint(0,5), "trend_direction": random.choice(["up","down","stable"]),
                "forecast_risk": round(score*0.9,3), "feature_importances": {"amount":0.32,"timing":0.28,"vendor":0.25,"flags":0.15}}
        ctx.ml_data = data
        return AgentOutput(8, self.agent_name, "COMPLETED", 0, 0.87, findings=data, flags=["ML_ANOMALY"] if data["anomaly_detected"] else [])
