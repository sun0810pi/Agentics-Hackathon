"""
backend/agents/tier1_core/agent_3_ai_analyst.py — AI Risk Scoring via Bedrock

PERF FIX:
  - boto3 / json / re imports moved to top-level (not inside _execute)
  - boto3 client cached as class attribute
  - Log "Bedrock failed" only once (không spam mỗi request)
"""
import os, json, re, random, logging
from typing import Optional
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier

logger = logging.getLogger(__name__)

# Lazy-import boto3 once
try:
    import boto3 as _boto3
    _BOTO3_OK = True
except ImportError:
    _boto3 = None
    _BOTO3_OK = False


class Agent3AIAnalyst(BaseAgent):
    agent_id = 3; agent_name = "AI Analyst"; tier = AgentTier.CORE

    # PERF: cached Bedrock client — created once per Lambda lifetime
    _bedrock_client = None
    _bedrock_warned  = False

    def _get_bedrock(self):
        if not _BOTO3_OK:
            return None
        if self._bedrock_client is None:
            try:
                Agent3AIAnalyst._bedrock_client = _boto3.client(
                    "bedrock-runtime",
                    region_name=os.getenv("AWS_REGION", "us-east-1"),
                )
            except Exception:
                pass
        return self._bedrock_client

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        if self._demo_mode(ctx):
            data = self._demo_score(ctx)
            ctx.risk_data = data
            flags = ["HIGH_RISK"] if data["risk_score"] >= 70 else []
            return AgentOutput(3, self.agent_name, "COMPLETED", 0, data["confidence"],
                               findings=data, flags=flags)

        bedrock = self._get_bedrock()
        if bedrock is None:
            if not Agent3AIAnalyst._bedrock_warned:
                logger.warning("boto3/Bedrock not available — using rule-based scoring (log once)")
                Agent3AIAnalyst._bedrock_warned = True
            data = self._rule_score(ctx)
            ctx.risk_data = data
            return AgentOutput(3, self.agent_name, "COMPLETED", 0, data["confidence"],
                               findings=data, flags=["HIGH_RISK"] if data["risk_score"] >= 70 else [])

        try:
            resp = bedrock.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 512,
                    "messages": [{"role": "user", "content": self._prompt(ctx)}],
                }),
                contentType="application/json",
                accept="application/json",
            )
            text = json.loads(resp["body"].read())["content"][0]["text"]
            m    = re.search(r'\{.*\}', text, re.DOTALL)
            data = json.loads(m.group()) if m else self._rule_score(ctx)
        except Exception as e:
            logger.warning(f"Bedrock invoke failed: {e} — rule-based fallback")
            data = self._rule_score(ctx)

        ctx.risk_data = data
        return AgentOutput(3, self.agent_name, "COMPLETED", 0, data.get("confidence", 0.8),
                           findings=data,
                           flags=["HIGH_RISK"] if data.get("risk_score", 0) >= 70 else [])

    def _prompt(self, ctx: AgentContext) -> str:
        return (
            f"You are a financial fraud detection AI. Analyze this invoice and return ONLY valid JSON.\n"
            f"Invoice: vendor={ctx.extracted.get('vendor_name')}, "
            f"amount=${ctx.extracted.get('total_amount')}, flags={ctx.fraud_flags}\n"
            f'Return: {{"risk_score":0-100,"risk_level":"LOW|MEDIUM|HIGH|CRITICAL",'
            f'"decision":"APPROVE|REVIEW|BLOCK","confidence":0.0-1.0,'
            f'"risk_factors":[],"explanation":""}}'
        )

    def _rule_score(self, ctx: AgentContext) -> dict:
        score = min(
            sum(25 if "MISMATCH" in f else 15 if "LARGE" in f else 10 for f in ctx.fraud_flags),
            100
        )
        if ctx.extracted.get("ocr_confidence", 1.0) < 0.7:
            score = min(score + 20, 100)
        level = "CRITICAL" if score >= 85 else "HIGH" if score >= 70 else "MEDIUM" if score >= 30 else "LOW"
        return {
            "risk_score":    score,
            "risk_level":    level,
            "decision":      "BLOCK" if score >= 70 else "REVIEW" if score >= 30 else "APPROVE",
            "confidence":    0.80,
            "risk_factors":  ctx.fraud_flags.copy(),
            "explanation":   f"Rule-based score: {score}/100",
            "bedrock_model": "rule-based-fallback",
        }

    def _demo_score(self, ctx: AgentContext) -> dict:
        n = len(ctx.fraud_flags)
        if n == 0:    score, decision, level = random.randint(5, 28),  "APPROVE", "LOW"
        elif n == 1:  score, decision, level = random.randint(30, 55), "REVIEW",  "MEDIUM"
        else:         score, decision, level = random.randint(70, 95), "BLOCK",   "HIGH"
        return {
            "risk_score":    score,
            "risk_level":    level,
            "decision":      decision,
            "confidence":    round(random.uniform(0.82, 0.97), 3),
            "risk_factors":  ctx.fraud_flags.copy() or ["No significant risk factors"],
            "explanation":   f"AI analysis: {level} risk. Score {score}/100.",
            "bedrock_model": "claude-3-sonnet (demo)",
        }
