# =====================================================
# backend/services/aws_service.py
# AWS Service Integrations:
# - AWS Textract: OCR for invoice extraction
# - AWS Bedrock (Claude): AI risk analysis
# - AWS S3: File storage
# =====================================================

import json
import logging
import os
import time
from typing import Dict, Any, Optional, List

import boto3
from botocore.exceptions import ClientError

from services.xray_tracer import tracer

logger = logging.getLogger(__name__)

# AWS region
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "agentflow-invoices")

# Bedrock model ID (Claude Haiku for cost efficiency, Claude Sonnet for accuracy)
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-3-haiku-20240307-v1:0"
)


class TextractService:
    """
    AWS Textract OCR for invoice data extraction.
    Extracts: tables, key-value pairs, plain text from PDFs/images.
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = boto3.client("textract", region_name=AWS_REGION)
        return self._client

    @tracer.capture("textract_analyze")
    def analyze_document(self, file_bytes: bytes, file_type: str = "PDF") -> Dict[str, Any]:
        """
        Run Textract AnalyzeDocument on invoice file.

        Args:
            file_bytes: Raw file content
            file_type: "PDF" or "IMAGE"

        Returns:
            Dict with extracted fields, tables, raw text
        """
        try:
            client = self._get_client()
            response = client.analyze_document(
                Document={"Bytes": file_bytes},
                FeatureTypes=["FORMS", "TABLES"],  # Extract key-value pairs and tables
            )

            return self._parse_textract_response(response)

        except ClientError as e:
            logger.error(f"Textract error: {e.response['Error']['Code']}: {e}")
            # Return empty extraction on failure
            return {
                "raw_text": "",
                "key_value_pairs": {},
                "tables": [],
                "confidence": 0.0,
                "error": str(e),
            }

    def _parse_textract_response(self, response: Dict) -> Dict[str, Any]:
        """Parse raw Textract response into structured data."""
        blocks = response.get("Blocks", [])

        # Build block map for fast lookup
        block_map = {b["Id"]: b for b in blocks}

        # Extract raw text
        raw_text = " ".join(
            b["Text"] for b in blocks
            if b["BlockType"] == "LINE" and "Text" in b
        )

        # Extract key-value pairs (form fields)
        key_value_pairs = {}
        confidence_scores = []

        for block in blocks:
            if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", []):
                key_text, val_text, conf = self._extract_kv(block, block_map)
                if key_text:
                    key_value_pairs[key_text.lower().strip()] = val_text.strip()
                    confidence_scores.append(conf)

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        # Map common invoice fields
        invoice_fields = self._map_invoice_fields(key_value_pairs, raw_text)

        return {
            "raw_text": raw_text,
            "key_value_pairs": key_value_pairs,
            "invoice_fields": invoice_fields,
            "confidence": avg_confidence,
        }

    def _extract_kv(self, key_block, block_map):
        """Extract key-value pair from Textract blocks."""
        key_text = ""
        val_text = ""
        confidence = key_block.get("Confidence", 0) / 100.0

        for rel in key_block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for word_id in rel["Ids"]:
                    word = block_map.get(word_id, {})
                    if word.get("BlockType") == "WORD":
                        key_text += word.get("Text", "") + " "
            elif rel["Type"] == "VALUE":
                for val_id in rel["Ids"]:
                    val_block = block_map.get(val_id, {})
                    for child_rel in val_block.get("Relationships", []):
                        if child_rel["Type"] == "CHILD":
                            for word_id in child_rel["Ids"]:
                                word = block_map.get(word_id, {})
                                if word.get("BlockType") == "WORD":
                                    val_text += word.get("Text", "") + " "

        return key_text, val_text, confidence

    def _map_invoice_fields(self, kv_pairs: Dict, raw_text: str) -> Dict[str, Any]:
        """Map Textract key-value pairs to standard invoice fields."""
        import re

        fields = {}

        # Invoice number patterns
        for key in ["invoice number", "invoice no", "invoice #", "inv no", "invoice id"]:
            if key in kv_pairs:
                fields["invoice_number"] = kv_pairs[key]
                break

        # Vendor/supplier name
        for key in ["vendor", "supplier", "from", "bill from", "company"]:
            if key in kv_pairs:
                fields["vendor_name"] = kv_pairs[key]
                break

        # Total amount - look for currency patterns in raw text
        amount_pattern = r'\$[\d,]+\.?\d*|\d+[,.]?\d*\s*(?:USD|EUR|VND)'
        amounts = re.findall(amount_pattern, raw_text)
        if amounts:
            # Take the largest amount as likely total
            def parse_amount(a):
                return float(re.sub(r'[^\d.]', '', a) or 0)
            fields["amount_total"] = max(amounts, key=parse_amount)

        # Date
        for key in ["date", "invoice date", "issued date"]:
            if key in kv_pairs:
                fields["invoice_date"] = kv_pairs[key]
                break

        # PO Number
        for key in ["po number", "purchase order", "po #", "p.o."]:
            if key in kv_pairs:
                fields["po_number"] = kv_pairs[key]
                break

        return fields


class BedrockService:
    """
    AWS Bedrock (Claude) for AI-powered fraud risk analysis.
    Uses Claude to reason about invoice anomalies.
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=AWS_REGION
            )
        return self._client

    @tracer.capture("bedrock_analyze")
    def analyze_fraud_risk(
        self,
        invoice_data: Dict[str, Any],
        historical_context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Use Claude via Bedrock to analyze fraud risk.

        Args:
            invoice_data: Extracted invoice fields
            historical_context: Historical data for this vendor (optional)

        Returns:
            Dict with risk_score, reasoning, flags, confidence
        """
        prompt = self._build_analysis_prompt(invoice_data, historical_context)

        try:
            client = self._get_client()
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            })

            response = client.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                body=body,
                contentType="application/json",
                accept="application/json",
            )

            result_body = json.loads(response["body"].read())
            text_response = result_body["content"][0]["text"]

            return self._parse_ai_response(text_response)

        except ClientError as e:
            logger.error(f"Bedrock error: {e}")
            # Fallback: rule-based scoring
            return self._rule_based_fallback(invoice_data)

    def _build_analysis_prompt(self, invoice_data: Dict, context: Optional[Dict]) -> str:
        """Build structured prompt for Claude fraud analysis."""
        context_str = ""
        if context:
            context_str = f"""
Historical vendor data:
- Average invoice amount: {context.get('avg_amount', 'unknown')}
- Previous invoices: {context.get('invoice_count', 0)}
- Last invoice date: {context.get('last_invoice_date', 'unknown')}
- Known fraud flags: {context.get('fraud_history', 'none')}
"""

        return f"""You are a fraud detection expert analyzing an invoice.

Invoice Data:
{json.dumps(invoice_data, indent=2)}

{context_str}

Analyze this invoice for fraud indicators. Consider:
1. Amount anomalies (unusually high/low, round numbers)
2. Vendor legitimacy signals
3. Date inconsistencies
4. Missing required fields
5. Duplicate invoice risk
6. Amount manipulation patterns

Respond ONLY with valid JSON in this exact format:
{{
  "risk_score": <0-100 integer, higher = more risky>,
  "decision": <"APPROVE" | "REVIEW" | "BLOCK">,
  "confidence": <0.0-1.0 float>,
  "reasoning": "<brief explanation>",
  "flags": ["<flag1>", "<flag2>"],
  "anomalies": {{
    "amount": "<normal|suspicious|anomalous>",
    "vendor": "<verified|unverified|suspicious>",
    "dates": "<consistent|inconsistent>",
    "completeness": "<complete|incomplete|missing_critical>"
  }}
}}"""

    def _parse_ai_response(self, text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response."""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback if parsing fails
        return {
            "risk_score": 50,
            "decision": "REVIEW",
            "confidence": 0.5,
            "reasoning": "AI analysis unavailable - manual review required",
            "flags": ["AI_PARSE_ERROR"],
            "anomalies": {},
        }

    def _rule_based_fallback(self, invoice_data: Dict) -> Dict[str, Any]:
        """
        Simple rule-based scoring when Bedrock unavailable.
        Used for local dev or Bedrock outages.
        """
        risk_score = 20  # Base score
        flags = []

        amount = invoice_data.get("amount_total")
        if amount:
            try:
                amt = float(str(amount).replace(",", "").replace("$", ""))
                if amt > 100000:
                    risk_score += 30
                    flags.append("LARGE_AMOUNT")
                if amt % 1000 == 0:
                    risk_score += 10
                    flags.append("ROUND_AMOUNT")
            except (ValueError, TypeError):
                risk_score += 15
                flags.append("INVALID_AMOUNT_FORMAT")

        if not invoice_data.get("vendor_name"):
            risk_score += 20
            flags.append("MISSING_VENDOR")

        if not invoice_data.get("invoice_number"):
            risk_score += 15
            flags.append("MISSING_INVOICE_NUMBER")

        decision = "APPROVE" if risk_score < 30 else ("BLOCK" if risk_score >= 70 else "REVIEW")

        return {
            "risk_score": min(risk_score, 100),
            "decision": decision,
            "confidence": 0.6,
            "reasoning": "Rule-based analysis (Bedrock unavailable)",
            "flags": flags,
            "anomalies": {},
        }


class S3Service:
    """S3 file storage for invoice documents."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = boto3.client("s3", region_name=AWS_REGION)
        return self._client

    def upload_invoice(self, invoice_id: str, file_bytes: bytes, content_type: str) -> str:
        """
        Upload invoice to S3 with encryption.
        Returns S3 key for the uploaded file.
        """
        key = f"invoices/{invoice_id}/original"
        try:
            self._get_client().put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=file_bytes,
                ContentType=content_type,
                ServerSideEncryption="aws:kms",  # KMS encryption at rest
                Metadata={
                    "invoice_id": invoice_id,
                    "uploaded_at": str(time.time()),
                },
            )
            logger.info(f"Invoice {invoice_id} uploaded to S3: {key}")
            return key
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return ""


# Global service instances
textract_service = TextractService()
bedrock_service = BedrockService()
s3_service = S3Service()
