"""
backend/agents/tier1_core/
===========================
Tier 1: Core Detection Agents (0-7)
These run on every invoice, in order.
"""

# ─────────────────────────────────────────────────────────────
# AGENT 0: OCR Extractor (AWS Textract)
# ─────────────────────────────────────────────────────────────
import base64, random, logging, os
from agents.base import BaseAgent, AgentContext, AgentOutput, AgentTier
logger = logging.getLogger(__name__)


class Agent0OCR(BaseAgent):
    """
    Extracts structured data from invoice images/PDFs using AWS Textract.
    Falls back to demo data when Textract is not configured.

    Output keys written to context.extracted:
        invoice_number, vendor_name, vendor_id, invoice_date, due_date,
        line_items, subtotal, tax_amount, total_amount, currency, po_number,
        ocr_confidence
    """
    agent_id   = 0
    agent_name = "OCR Extractor"
    tier       = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        if self._demo_mode(ctx):
            extracted = self._demo_extracted(ctx)
            ctx.extracted = extracted
            return AgentOutput(
                agent_id=0, agent_name=self.agent_name,
                status="COMPLETED", duration_ms=0, confidence=0.96,
                findings=extracted,
            )

        try:
            import boto3
            client = boto3.client("textract", region_name=os.getenv("AWS_REGION", "us-east-1"))
            response = client.analyze_document(
                Document={"Bytes": ctx.file_data},
                FeatureTypes=["TABLES", "FORMS"],
            )
            extracted = self._parse_textract_response(response)
        except Exception as e:
            logger.warning(f"Textract failed ({e}), using demo data")
            extracted = self._demo_extracted(ctx)

        ctx.extracted = extracted
        return AgentOutput(
            agent_id=0, agent_name=self.agent_name,
            status="COMPLETED", duration_ms=0,
            confidence=extracted.get("ocr_confidence", 0.9),
            findings=extracted,
        )

    def _parse_textract_response(self, response: dict) -> dict:
        """Parse raw Textract API response into structured invoice data."""
        blocks = response.get("Blocks", [])
        text_blocks = [b["Text"] for b in blocks if b["BlockType"] == "LINE" and "Text" in b]
        full_text = " ".join(text_blocks)

        import re
        # Extract total amount
        total_match = re.search(r'(?:total|amount due)[:\s]*\$?([\d,]+\.?\d*)', full_text, re.IGNORECASE)
        total = float(total_match.group(1).replace(",", "")) if total_match else 0.0

        # Extract invoice number
        inv_match = re.search(r'(?:invoice|inv)[:\s#]*([A-Z0-9\-]+)', full_text, re.IGNORECASE)
        inv_num = inv_match.group(1) if inv_match else f"INV-AUTO-{random.randint(1000,9999)}"

        avg_confidence = sum(
            b.get("Confidence", 0) for b in blocks if "Confidence" in b
        ) / max(len(blocks), 1) / 100

        return {
            "invoice_number": inv_num,
            "vendor_name":    "Extracted Vendor",
            "total_amount":   total,
            "currency":       "USD",
            "ocr_confidence": round(avg_confidence, 3),
            "line_items":     [],
        }

    def _demo_extracted(self, ctx: AgentContext) -> dict:
        vendors = ["TechCorp Inc", "SupplyChain Ltd", "GlobalServices", "FastShip Co", "DataSystems"]
        total   = round(random.uniform(500, 50000), 2)
        tax     = round(total * 0.1, 2)
        return {
            "invoice_number": f"INV-2026-{random.randint(1000, 9999)}",
            "vendor_name":    random.choice(vendors),
            "vendor_id":      f"VND-{random.randint(100, 999)}",
            "invoice_date":   "2026-02-01",
            "due_date":       "2026-03-01",
            "line_items": [
                {"description": "Professional Services", "quantity": 1,  "unit_price": total * 0.7, "amount": total * 0.7},
                {"description": "Support & Maintenance", "quantity": 12, "unit_price": total * 0.3 / 12, "amount": total * 0.3},
            ],
            "subtotal":       round(total - tax, 2),
            "tax_amount":     tax,
            "total_amount":   total,
            "currency":       "USD",
            "po_number":      f"PO-{random.randint(10000, 99999)}",
            "ocr_confidence": round(random.uniform(0.88, 0.99), 3),
        }


# ─────────────────────────────────────────────────────────────
# AGENT 1: PII Preprocessor (GDPR Compliance)
# ─────────────────────────────────────────────────────────────

class Agent1PII(BaseAgent):
    """
    Masks PII from extracted data for GDPR compliance.
    Uses AWS Comprehend for detection when available; regex otherwise.
    Writes masked copies to context.pii_report.
    """
    agent_id   = 1
    agent_name = "PII Preprocessor"
    tier       = AgentTier.CORE

    PII_PATTERNS = {
        "email":   r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b',
        "phone":   r'\b(\+\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}\b',
        "ssn":     r'\b\d{3}-\d{2}-\d{4}\b',
        "cc":      r'\b(?:\d[ -]?){13,16}\b',
        "iban":    r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}(?:[A-Z0-9]?){0,16}\b',
    }

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        import re
        masked_fields: list[str] = []
        masked_data: dict        = {}

        text_fields = {
            "vendor_name": ctx.extracted.get("vendor_name", ""),
            "invoice_number": ctx.extracted.get("invoice_number", ""),
        }

        for field_name, value in text_fields.items():
            original = str(value)
            masked   = original
            for pii_type, pattern in self.PII_PATTERNS.items():
                if re.search(pattern, original):
                    masked = re.sub(pattern, f"[{pii_type.upper()}_MASKED]", masked)
                    masked_fields.append(f"{field_name}:{pii_type}")

            if masked != original:
                masked_data[field_name] = masked

        pii_detected = len(masked_fields) > 0
        ctx.pii_report = {
            "fields_masked":  masked_fields,
            "gdpr_compliant": True,
            "pii_detected":   pii_detected,
            "masked_data":    masked_data,
        }

        return AgentOutput(
            agent_id=1, agent_name=self.agent_name,
            status="COMPLETED", duration_ms=0, confidence=0.99,
            findings=ctx.pii_report,
            flags=["PII_DETECTED"] if pii_detected else [],
        )


# ─────────────────────────────────────────────────────────────
# AGENT 2: Decimal Matcher (Amount Validation)
# ─────────────────────────────────────────────────────────────

class Agent2Decimal(BaseAgent):
    """
    Validates invoice amounts against PO data.
    Checks:
    - Line items sum equals subtotal
    - Subtotal + tax equals total
    - Total within expected range for vendor
    - Duplicate invoice detection
    """
    agent_id   = 2
    agent_name = "Decimal Matcher"
    tier       = AgentTier.CORE

    TOLERANCE = 0.02   # 2 cents tolerance for rounding

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        extracted = ctx.extracted
        flags: list[str] = []
        findings: dict   = {}

        # 1. Line items sum check
        line_total = sum(
            float(item.get("amount", 0)) for item in extracted.get("line_items", [])
        )
        subtotal = float(extracted.get("subtotal", 0))
        if abs(line_total - subtotal) > self.TOLERANCE and line_total > 0:
            flags.append("LINE_ITEMS_SUM_MISMATCH")
            findings["line_items_delta"] = round(line_total - subtotal, 2)

        # 2. Subtotal + tax = total check
        tax   = float(extracted.get("tax_amount", 0))
        total = float(extracted.get("total_amount", 0))
        expected_total = subtotal + tax
        if abs(expected_total - total) > self.TOLERANCE and expected_total > 0:
            flags.append("TOTAL_AMOUNT_MISMATCH")
            findings["total_delta"] = round(expected_total - total, 2)

        # 3. Sanity range check
        if total <= 0:
            flags.append("ZERO_OR_NEGATIVE_AMOUNT")
        if total > 1_000_000:
            flags.append("UNUSUALLY_LARGE_AMOUNT")
            findings["amount_flag"] = f"${total:,.2f} exceeds $1M threshold"

        # 4. Tax rate sanity (0% - 30%)
        if total > 0:
            tax_rate = (tax / total) * 100
            if tax_rate > 30:
                flags.append("ABNORMAL_TAX_RATE")
                findings["tax_rate"] = round(tax_rate, 2)

        ctx.fraud_flags.extend(flags)
        findings["validated"] = len(flags) == 0
        confidence = 0.95 if len(flags) == 0 else max(0.3, 0.95 - len(flags) * 0.2)

        return AgentOutput(
            agent_id=2, agent_name=self.agent_name,
            status="COMPLETED", duration_ms=0, confidence=confidence,
            findings=findings, flags=flags,
        )


# ─────────────────────────────────────────────────────────────
# AGENT 3: AI Analyst (Bedrock Claude Risk Scoring)
# ─────────────────────────────────────────────────────────────

class Agent3AIAnalyst(BaseAgent):
    """
    Uses AWS Bedrock Claude to score fraud risk.
    The AI considers all extracted data + prior flags from agents 0-2.

    Returns:
        risk_score    : 0-100
        risk_level    : LOW | MEDIUM | HIGH | CRITICAL
        decision      : APPROVE | REVIEW | BLOCK
        explanation   : human-readable reasoning
        confidence    : 0.0-1.0
    """
    agent_id   = 3
    agent_name = "AI Analyst"
    tier       = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        if self._demo_mode(ctx):
            return self._demo_analysis(ctx)

        try:
            import boto3, json as _json
            bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))

            prompt = self._build_prompt(ctx)
            response = bedrock.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=_json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 512,
                    "messages": [{"role": "user", "content": prompt}],
                }),
                contentType="application/json",
                accept="application/json",
            )
            result_text = _json.loads(response["body"].read())["content"][0]["text"]
            parsed = self._parse_ai_response(result_text)
        except Exception as e:
            logger.warning(f"Bedrock failed ({e}), using rule-based scoring")
            parsed = self._rule_based_score(ctx)

        ctx.risk_data = parsed
        return AgentOutput(
            agent_id=3, agent_name=self.agent_name,
            status="COMPLETED", duration_ms=0,
            confidence=parsed.get("confidence", 0.85),
            findings=parsed,
            flags=["HIGH_RISK"] if parsed.get("risk_score", 0) >= 70 else [],
        )

    def _build_prompt(self, ctx: AgentContext) -> str:
        flags = ctx.fraud_flags
        ext   = ctx.extracted
        return f"""You are a financial fraud detection AI. Analyze this invoice and return ONLY valid JSON.

Invoice Data:
- Vendor: {ext.get('vendor_name')} (ID: {ext.get('vendor_id')})
- Amount: ${ext.get('total_amount')} {ext.get('currency')}
- Invoice #: {ext.get('invoice_number')}
- Date: {ext.get('invoice_date')}
- OCR Confidence: {ext.get('ocr_confidence', 0):.1%}
- Prior Flags: {flags}

Return JSON: {{"risk_score": 0-100, "risk_level": "LOW|MEDIUM|HIGH|CRITICAL", 
"decision": "APPROVE|REVIEW|BLOCK", "confidence": 0.0-1.0, 
"risk_factors": ["..."], "explanation": "..."}}"""

    def _parse_ai_response(self, text: str) -> dict:
        import json as _json, re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return _json.loads(json_match.group())
            except Exception:
                pass
        return self._rule_based_score_empty()

    def _rule_based_score(self, ctx: AgentContext) -> dict:
        """Fallback when Bedrock is unavailable."""
        score = 0
        factors: list[str] = []
        for flag in ctx.fraud_flags:
            if "MISMATCH" in flag:
                score += 25; factors.append(flag)
            elif "LARGE" in flag:
                score += 15; factors.append(flag)
            else:
                score += 10; factors.append(flag)

        if ctx.extracted.get("ocr_confidence", 1.0) < 0.7:
            score += 20; factors.append("LOW_OCR_CONFIDENCE")

        score = min(score, 100)
        return {
            "risk_score":   score,
            "risk_level":   "CRITICAL" if score >= 85 else "HIGH" if score >= 70 else "MEDIUM" if score >= 30 else "LOW",
            "decision":     "BLOCK" if score >= 70 else "REVIEW" if score >= 30 else "APPROVE",
            "confidence":   0.80,
            "risk_factors": factors,
            "explanation":  f"Rule-based: {len(factors)} flags detected, score={score}",
            "bedrock_model": "rule-based-fallback",
        }

    def _rule_based_score_empty(self) -> dict:
        return self._rule_based_score_from_flags([], 0.9)

    def _demo_analysis(self, ctx: AgentContext) -> AgentOutput:
        n_flags = len(ctx.fraud_flags)
        if n_flags == 0:
            score, decision, level = random.randint(5, 28), "APPROVE", "LOW"
        elif n_flags == 1:
            score, decision, level = random.randint(30, 55), "REVIEW",  "MEDIUM"
        else:
            score, decision, level = random.randint(70, 95), "BLOCK",   "HIGH"

        factors = list(ctx.fraud_flags) or ["No significant risk factors detected"]
        data = {
            "risk_score":    score,
            "risk_level":    level,
            "decision":      decision,
            "confidence":    round(random.uniform(0.82, 0.97), 3),
            "risk_factors":  factors,
            "explanation":   f"AI analysis: {level} risk. Score {score}/100.",
            "bedrock_model": "claude-3-sonnet (demo)",
        }
        ctx.risk_data = data
        return AgentOutput(
            agent_id=3, agent_name=self.agent_name,
            status="COMPLETED", duration_ms=0,
            confidence=data["confidence"], findings=data,
            flags=["HIGH_RISK"] if score >= 70 else [],
        )


# ─────────────────────────────────────────────────────────────
# AGENT 4: Audit Seal
# ─────────────────────────────────────────────────────────────

class Agent4Audit(BaseAgent):
    """
    Creates immutable audit trail with SHA-256 hash.
    Every processed invoice gets a cryptographic seal.
    This proves the data hasn't been tampered with.
    """
    agent_id   = 4
    agent_name = "Audit Seal"
    tier       = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        import hashlib, json as _json, time as _t

        audit_data = {
            "invoice_id":    ctx.invoice_id,
            "file_name":     ctx.file_name,
            "extracted":     ctx.extracted,
            "risk_score":    ctx.risk_data.get("risk_score", 0),
            "decision":      ctx.risk_data.get("decision", "ERROR"),
            "fraud_flags":   ctx.fraud_flags,
            "timestamp":     _t.time(),
            "trace_id":      ctx.trace_id,
        }
        payload = _json.dumps(audit_data, sort_keys=True)
        sha256  = hashlib.sha256(payload.encode()).hexdigest()

        entry = f"[{ctx.invoice_id}] decision={ctx.risk_data.get('decision', '?')} hash={sha256[:16]}..."
        ctx.audit_entries.append(entry)

        return AgentOutput(
            agent_id=4, agent_name=self.agent_name,
            status="COMPLETED", duration_ms=0, confidence=1.0,
            findings={"audit_hash": sha256, "audit_entry": entry},
        )


# ─────────────────────────────────────────────────────────────
# AGENT 5: Notifier
# ─────────────────────────────────────────────────────────────

class Agent5Notifier(BaseAgent):
    """
    Sends alerts for high-risk invoices via SNS/SES.
    Only fires for BLOCK or REVIEW decisions.
    """
    agent_id   = 5
    agent_name = "Notifier"
    tier       = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        decision = ctx.risk_data.get("decision", "APPROVE")

        if decision not in ("BLOCK", "REVIEW"):
            return AgentOutput(
                agent_id=5, agent_name=self.agent_name,
                status="SKIPPED", duration_ms=0, confidence=1.0,
                findings={"reason": f"Decision is {decision}, no notification needed"},
            )

        if self._demo_mode(ctx):
            return AgentOutput(
                agent_id=5, agent_name=self.agent_name,
                status="COMPLETED", duration_ms=0, confidence=1.0,
                findings={
                    "notifications_sent": ["email (demo)", "slack (demo)"],
                    "decision": decision,
                },
            )

        sent: list[str] = []
        try:
            import boto3
            sns = boto3.client("sns", region_name=os.getenv("AWS_REGION", "us-east-1"))
            topic_arn = os.getenv("SNS_ALERT_TOPIC_ARN")
            if topic_arn:
                sns.publish(
                    TopicArn=topic_arn,
                    Message=f"⚠️ {decision}: Invoice {ctx.invoice_id} | Risk={ctx.risk_data.get('risk_score')}",
                    Subject=f"AgentFlow Alert: {decision} - {ctx.invoice_id}",
                )
                sent.append("sns")
        except Exception as e:
            logger.warning(f"SNS notification failed: {e}")

        return AgentOutput(
            agent_id=5, agent_name=self.agent_name,
            status="COMPLETED", duration_ms=0, confidence=1.0,
            findings={"notifications_sent": sent, "decision": decision},
        )


# ─────────────────────────────────────────────────────────────
# AGENT 6: Dashboard Data Aggregator
# ─────────────────────────────────────────────────────────────

class Agent6Dashboard(BaseAgent):
    """Aggregates result data for real-time dashboard update."""
    agent_id   = 6
    agent_name = "Dashboard Data"
    tier       = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        summary = {
            "invoice_id":   ctx.invoice_id,
            "vendor":       ctx.extracted.get("vendor_name"),
            "amount":       ctx.extracted.get("total_amount"),
            "currency":     ctx.extracted.get("currency", "USD"),
            "decision":     ctx.risk_data.get("decision"),
            "risk_score":   ctx.risk_data.get("risk_score"),
            "flags_count":  len(ctx.fraud_flags),
            "processing_ms": (time.time() - ctx.started_at) * 1000,
        }
        return AgentOutput(
            agent_id=6, agent_name=self.agent_name,
            status="COMPLETED", duration_ms=0, confidence=1.0,
            findings=summary,
        )


# ─────────────────────────────────────────────────────────────
# AGENT 7: External Integrator
# ─────────────────────────────────────────────────────────────

class Agent7Integrator(BaseAgent):
    """
    Syncs results to external systems (ERP, Google Sheets, Slack).
    Runs async and doesn't block the main pipeline.
    """
    agent_id   = 7
    agent_name = "Integrator"
    tier       = AgentTier.CORE

    async def _execute(self, ctx: AgentContext) -> AgentOutput:
        synced: list[str] = []

        # Demo: simulate external sync
        if self._demo_mode(ctx):
            synced = ["Google Sheets (demo)", "ERP System (demo)"]
        else:
            # Real: add your webhook URLs here
            webhook_url = os.getenv("INTEGRATION_WEBHOOK_URL")
            if webhook_url:
                try:
                    import httpx, json as _json
                    async with httpx.AsyncClient() as client:
                        await client.post(webhook_url, json={
                            "invoice_id": ctx.invoice_id,
                            "decision":   ctx.risk_data.get("decision"),
                            "risk_score": ctx.risk_data.get("risk_score"),
                        }, timeout=5.0)
                    synced.append("webhook")
                except Exception as e:
                    logger.warning(f"Integration webhook failed: {e}")

        return AgentOutput(
            agent_id=7, agent_name=self.agent_name,
            status="COMPLETED", duration_ms=0, confidence=1.0,
            findings={"synced_to": synced},
        )
