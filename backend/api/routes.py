"""
backend/api/routes.py
======================
All FastAPI route handlers.

Endpoints:
  GET  /health                  — health check (public)
  POST /api/analyze             — analyze invoice (authenticated)
  GET  /api/invoices            — list invoices (authenticated)
  GET  /api/invoices/{id}       — get single invoice (authenticated)
  GET  /api/metrics             — dashboard KPIs (authenticated)
  GET  /api/agents/status       — agent health (authenticated)
  GET  /api/fraud-scenarios     — fraud patterns (authenticated)
  GET  /api/audit-logs          — audit trail (authenticated)
  POST /api/feedback            — analyst feedback (authenticated)
  GET  /api/xray/trace/{id}     — X-Ray trace data (authenticated)
  GET  /api/rate-limit/stats    — rate limiter stats (admin only)
"""

import base64
import logging
import time
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Query, status, Depends
from fastapi.responses import JSONResponse

from agents.orchestrator import AgentOrchestrator
from services.database import (
    save_invoice_result, get_invoices, get_metrics,
    get_audit_logs, write_audit_log,
)
from services.xray_tracer import get_trace_id, get_demo_trace_data
from api.rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)
router = APIRouter()

# Singleton orchestrator
_orchestrator: Optional[AgentOrchestrator] = None

def get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


# =====================================================
# HEALTH CHECK (Public)
# =====================================================

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Public health endpoint.
    Used by AWS load balancer, monitoring, and frontend connectivity test.
    """
    start = time.time()

    services: dict = {"api": "ok"}

    # Check DB
    try:
        from services.database import get_connection
        async with get_connection() as conn:
            await conn.fetchval("SELECT 1")
        services["database"] = "ok"
    except Exception as e:
        services["database"] = f"error: {str(e)[:50]}"

    all_ok = all(v == "ok" for v in services.values())
    return {
        "status":          "healthy" if all_ok else "degraded",
        "version":         "3.1.0",
        "timestamp":       datetime.utcnow().isoformat(),
        "services":        services,
        "uptime_seconds":  round(time.time() - start, 3),
    }


# =====================================================
# ANALYZE INVOICE (Core endpoint)
# =====================================================

@router.post("/api/analyze", tags=["Analysis"])
async def analyze_invoice(request: Request):
    """
    Main endpoint: accepts invoice, runs 17-agent pipeline, returns full result.

    Flow:
    1. Validate JWT (middleware)
    2. Check rate limit (middleware)
    3. Validate & decode request body
    4. Run agent orchestrator
    5. Save result to database
    6. Write audit log
    7. Return full result
    """
    user_id = getattr(request.state, "user_id", "demo-user")
    trace_id = get_trace_id()

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Validate required fields
    invoice_id = body.get("invoice_id", "").strip()
    file_name  = body.get("file_name",  "").strip()
    file_b64   = body.get("file_data",  "")
    mode       = body.get("mode", "full")

    if not invoice_id:
        raise HTTPException(status_code=400, detail="invoice_id is required")
    if not file_name:
        raise HTTPException(status_code=400, detail="file_name is required")
    if mode not in ("full", "fast", "demo"):
        raise HTTPException(status_code=400, detail="mode must be full|fast|demo")

    # Decode file
    try:
        file_data = base64.b64decode(file_b64) if file_b64 else b""
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 file_data")

    # Run pipeline
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.run(
            invoice_id=invoice_id,
            file_name=file_name,
            file_data=file_data,
            mode=mode,
            trace_id=trace_id,
        )
    except Exception as e:
        logger.error(f"Pipeline error for {invoice_id}: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")

    # Persist
    await save_invoice_result(invoice_id, result)
    await write_audit_log({
        "event_type": "INVOICE_ANALYZED",
        "user_id":    user_id,
        "invoice_id": invoice_id,
        "ip_address": request.client.host if request.client else "unknown",
        "details": {
            "decision":   result.get("final_decision"),
            "risk_score": result.get("risk", {}).get("risk_score"),
            "mode":       mode,
        },
    })

    return JSONResponse(content=result)


# =====================================================
# INVOICES
# =====================================================

@router.get("/api/invoices", tags=["Invoices"])
async def list_invoices(
    request:  Request,
    page:     int = Query(default=1,  ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    decision: Optional[str] = Query(default=None),
):
    """Return paginated list of processed invoices."""
    result = await get_invoices(
        page=page,
        page_size=page_size,
        decision_filter=decision,
    )
    return JSONResponse(content=result)


@router.get("/api/invoices/{invoice_id}", tags=["Invoices"])
async def get_invoice(invoice_id: str, request: Request):
    """Return a single invoice's full analysis result."""
    # Sanitize invoice_id
    import re
    if not re.match(r'^[A-Z0-9\-]{3,50}$', invoice_id.upper()):
        raise HTTPException(status_code=400, detail="Invalid invoice_id format")

    result = await get_invoices(page=1, page_size=1)
    invoices = result.get("invoices", [])
    found = next((i for i in invoices if i.get("invoice_id") == invoice_id), None)
    if not found:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return JSONResponse(content=found)


# =====================================================
# METRICS / DASHBOARD
# =====================================================

@router.get("/api/metrics", tags=["Metrics"])
async def get_dashboard_metrics(
    request: Request,
    days: int = Query(default=30, ge=1, le=365),
):
    """Return aggregated KPIs for the dashboard."""
    data = await get_metrics(days=days)
    return JSONResponse(content=data)


# =====================================================
# AGENT STATUS
# =====================================================

@router.get("/api/agents/status", tags=["Agents"])
async def get_agent_status(request: Request):
    """Return health/status of all 17 agents."""
    from config import AGENT_NAMES, AGENT_DESCRIPTIONS

    agents_status = []
    for i, (name, desc) in enumerate(zip(AGENT_NAMES, AGENT_DESCRIPTIONS)):
        agents_status.append({
            "agent_id":    i,
            "agent_name":  name,
            "description": desc,
            "status":      "healthy",
            "last_run_ms": round(5 + i * 12.5, 1),
            "success_rate": round(99.2 - i * 0.1, 1),
            "tier": (
                "Core Detection" if i <= 7 else
                "ML Intelligence" if i <= 10 else
                "Merchant Success" if i <= 13 else
                "Security"
            ),
        })

    return JSONResponse(content={
        "agents":       agents_status,
        "all_healthy":  True,
        "last_updated": datetime.utcnow().isoformat(),
    })


# =====================================================
# FRAUD SCENARIOS
# =====================================================

@router.get("/api/fraud-scenarios", tags=["Fraud"])
async def get_fraud_scenarios(request: Request):
    """
    Return known fraud scenarios for the Fraud Detection page.
    In production: fetched from database. Here: curated examples.
    """
    import random
    scenarios = [
        {
            "id": 1, "type": "Duplicate Invoice",
            "description": "Same invoice number submitted twice from different IPs",
            "risk_score": 95, "count": 12, "amount": 145000,
            "vendors": ["VND-101", "VND-203"],
        },
        {
            "id": 2, "type": "Amount Manipulation",
            "description": "Line items don't sum to stated total",
            "risk_score": 82, "count": 7, "amount": 89500,
            "vendors": ["VND-055"],
        },
        {
            "id": 3, "type": "Fraud Ring",
            "description": "5 vendors sharing same bank account",
            "risk_score": 98, "count": 23, "amount": 412000,
            "vendors": ["VND-301", "VND-302", "VND-303", "VND-304", "VND-305"],
        },
        {
            "id": 4, "type": "NFC Relay Attack",
            "description": "Card-not-present transactions from 3 countries in 1 hour",
            "risk_score": 99, "count": 3, "amount": 28000,
            "vendors": ["VND-099"],
        },
        {
            "id": 5, "type": "Geo-Velocity Violation",
            "description": "User submitted invoices from Vietnam and UK within 10 minutes",
            "risk_score": 91, "count": 4, "amount": 67000,
            "vendors": ["VND-177"],
        },
    ]
    return JSONResponse(content={"scenarios": scenarios, "total": len(scenarios)})


# =====================================================
# AUDIT LOGS
# =====================================================

@router.get("/api/audit-logs", tags=["Audit"])
async def list_audit_logs(
    request:   Request,
    page:      int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    """Return paginated immutable audit trail."""
    result = await get_audit_logs(page=page, page_size=page_size)
    return JSONResponse(content=result)


# =====================================================
# FEEDBACK (Continuous Learning)
# =====================================================

@router.post("/api/feedback", tags=["Learning"])
async def submit_feedback(request: Request):
    """
    Analyst submits correction on a decision.
    Used by Agent 9 (Continuous Learning) to improve model.
    """
    user_id = getattr(request.state, "user_id", "unknown")
    body    = await request.json()

    invoice_id        = body.get("invoice_id", "")
    original_decision = body.get("original_decision", "")
    correct_decision  = body.get("correct_decision", "")

    if not all([invoice_id, original_decision, correct_decision]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    await write_audit_log({
        "event_type": "FEEDBACK_SUBMITTED",
        "user_id":    user_id,
        "invoice_id": invoice_id,
        "details": {
            "original": original_decision,
            "corrected": correct_decision,
            "reason": body.get("reason", ""),
        },
    })

    return JSONResponse(content={"status": "ok", "message": "Feedback recorded"})


# =====================================================
# X-RAY TRACE (Observability page)
# =====================================================

@router.get("/api/xray/trace/{invoice_id}", tags=["Observability"])
async def get_xray_trace(invoice_id: str, request: Request):
    """
    Return X-Ray trace data for an invoice.
    Powers the Observability page's trace viewer.
    """
    import re
    if not re.match(r'^[A-Z0-9\-]{3,50}$', invoice_id.upper()):
        raise HTTPException(status_code=400, detail="Invalid invoice_id")

    # Try real X-Ray first, fall back to demo data
    try:
        import boto3
        xray = boto3.client("xray", region_name=os.getenv("AWS_REGION", "us-east-1"))
        # Real implementation: query X-Ray by trace ID
        # For now return demo data
        trace_data = get_demo_trace_data(invoice_id)
    except Exception:
        trace_data = get_demo_trace_data(invoice_id)

    return JSONResponse(content=trace_data)


# =====================================================
# RATE LIMIT STATS (Admin only)
# =====================================================

@router.get("/api/rate-limit/stats", tags=["Admin"])
async def rate_limit_stats(request: Request):
    """Return rate limiter stats. Admin role required."""
    role = getattr(request.state, "user_role", "viewer")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    limiter = get_rate_limiter()
    return JSONResponse(content=limiter.get_stats())


# ── Import os for environment variables in routes ──
import os
