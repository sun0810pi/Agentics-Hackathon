# backend/agents/tier1_core/agent_0_ocr.py
"""Agent 0: OCR Extractor - Uses AWS Textract to extract invoice data"""
from agents.base import BaseAgent
from services.aws_service import textract_service
from typing import Dict, Any, List, Tuple


class Agent0OCR(BaseAgent):
    agent_id = 0
    agent_name = "OCR Extractor"
    tier = "Core Detection"

    async def _execute(self, invoice_data: Dict, context: Dict) -> Tuple[Dict, List[str], float]:
        file_bytes = context.get("file_bytes", b"")
        content_type = context.get("content_type", "application/pdf")
        flags = []

        if not file_bytes:
            return {}, ["NO_FILE_BYTES"], 0.0

        extraction = textract_service.analyze_document(file_bytes, content_type)
        confidence = extraction.get("confidence", 0.0)
        invoice_fields = extraction.get("invoice_fields", {})

        if confidence < 0.7:
            flags.append("LOW_OCR_CONFIDENCE")
        if not invoice_fields.get("invoice_number"):
            flags.append("MISSING_INVOICE_NUMBER")
        if not invoice_fields.get("amount_total"):
            flags.append("MISSING_AMOUNT")

        return {"invoice_fields": invoice_fields, "raw_text": extraction.get("raw_text", "")}, flags, confidence
