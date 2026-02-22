"""
backend/api/routes.py
======================
Tất cả API endpoints:
  GET  /health
  POST /api/analyze
  GET  /api/invoices
  GET  /api/invoices/{id}
  GET  /api/metrics
  GET  /api/agents/status
  GET  /api/fraud-scenarios
  GET  /api/audit-logs
  POST /api/feedback
  GET  /api/xray/trace/{id}
  GET  /api/rate-limit/stats   (admin)
"""

import base64, logging, time, uuid, os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from agents.orchestrator import AgentOrchestrator
from services.database import save_invoice_result, get_invoices, get_metrics, get_audit_logs, write_audit_log
from services.xray_tracer import get_trace_id, get_demo_trace_data
from api.rate_limiter import get_rate_limiter
import config

logger = logging.getLogger(__name__)
router = APIRouter()

_orch: Optional[AgentOrchestrator] = None
def get_orch() -> AgentOrchestrator:
    global _orch
    if _orch is None: _orch = AgentOrchestrator()
    return _orch


# ── Health ────────────────────────────────────────────────
@router.get("/health")
async def health():
    services = {"api": "ok"}
    try:
        from services.database import get_connection
        async with get_connection() as c: await c.fetchval("SELECT 1")
        services["database"] = "ok"
    except Exception as e:
        services["database"] = f"error: {str(e)[:40]}"
    ok = all(v == "ok" for v in services.values())
    return {"status": "healthy" if ok else "degraded", "version": config.APP_VERSION,
            "timestamp": datetime.utcnow().isoformat(), "services": services, "uptime_seconds": 0.0}


# ── Analyze ───────────────────────────────────────────────
@router.post("/api/analyze")
async def analyze(request: Request):
    user_id  = getattr(request.state, "user_id", "demo-user")
    trace_id = get_trace_id()

    try: body = await request.json()
    except Exception: raise HTTPException(400, "Invalid JSON")

    invoice_id = body.get("invoice_id", "").strip()
    file_name  = body.get("file_name",  "").strip()
    file_b64   = body.get("file_data",  "")
    mode       = body.get("mode", "demo")

    if not invoice_id: raise HTTPException(400, "invoice_id required")
    if not file_name:  raise HTTPException(400, "file_name required")
    if mode not in ("full","fast","demo"): raise HTTPException(400, "mode must be full|fast|demo")

    try:    file_data = base64.b64decode(file_b64) if file_b64 else b""
    except: raise HTTPException(400, "Invalid base64 file_data")

    try:
        result = await get_orch().run(invoice_id=invoice_id, file_name=file_name,
                                      file_data=file_data, mode=mode, trace_id=trace_id)
    except Exception as e:
        logger.error(f"Pipeline error {invoice_id}: {e}")
        raise HTTPException(500, "Processing failed")

    await save_invoice_result(invoice_id, result)
    await write_audit_log({"event_type":"INVOICE_ANALYZED","user_id":user_id,"invoice_id":invoice_id,
        "ip_address": request.client.host if request.client else "unknown",
        "details": {"decision": result.get("final_decision"), "risk_score": result.get("risk",{}).get("risk_score"), "mode": mode}})

    return JSONResponse(content=result)


# ── Invoices ──────────────────────────────────────────────
@router.get("/api/invoices")
async def list_invoices(request: Request,
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
    decision: Optional[str] = Query(None)):
    return JSONResponse(content=await get_invoices(page=page, page_size=page_size, decision_filter=decision))


@router.get("/api/invoices/{invoice_id}")
async def get_invoice(invoice_id: str, request: Request):
    import re
    if not re.match(r"^[A-Z0-9\-]{3,50}$", invoice_id.upper()):
        raise HTTPException(400, "Invalid invoice_id")
    result = await get_invoices(page=1, page_size=1)
    found = next((i for i in result.get("invoices",[]) if i.get("invoice_id") == invoice_id), None)
    if not found: raise HTTPException(404, "Invoice not found")
    return JSONResponse(content=found)


# ── Metrics ───────────────────────────────────────────────
@router.get("/api/metrics")
async def metrics(request: Request, days: int = Query(30, ge=1, le=365)):
    return JSONResponse(content=await get_metrics(days=days))


# ── Agents status ─────────────────────────────────────────
@router.get("/api/agents/status")
async def agent_status(request: Request):
    agents = [{"agent_id": i, "agent_name": n, "description": d, "status": "healthy",
               "last_run_ms": round(5+i*12.5,1), "success_rate": round(99.2-i*0.1,1),
               "tier": "Core Detection" if i<=7 else "ML Intelligence" if i<=10 else "Merchant Success" if i<=13 else "Security"}
              for i,(n,d) in enumerate(zip(config.AGENT_NAMES, config.AGENT_DESCRIPTIONS))]
    return JSONResponse(content={"agents": agents, "all_healthy": True, "last_updated": datetime.utcnow().isoformat()})


# ── Fraud Scenarios ───────────────────────────────────────
@router.get("/api/fraud-scenarios")
async def fraud_scenarios(request: Request):
    scenarios = [
        {"id":1,"type":"Duplicate Invoice","description":"Same invoice submitted twice from different IPs","risk_score":95,"count":12,"amount":145000},
        {"id":2,"type":"Amount Manipulation","description":"Line items don't sum to stated total","risk_score":82,"count":7,"amount":89500},
        {"id":3,"type":"Fraud Ring","description":"5 vendors sharing same bank account","risk_score":98,"count":23,"amount":412000},
        {"id":4,"type":"NFC Relay Attack","description":"Card-not-present transactions from 3 countries in 1 hour","risk_score":99,"count":3,"amount":28000},
        {"id":5,"type":"Geo-Velocity Violation","description":"User submitted from VN and UK within 10 minutes","risk_score":91,"count":4,"amount":67000},
    ]
    return JSONResponse(content={"scenarios": scenarios, "total": len(scenarios)})


# ── Audit Logs ────────────────────────────────────────────
@router.get("/api/audit-logs")
async def audit_logs(request: Request, page: int = Query(1,ge=1), page_size: int = Query(50,ge=1,le=200)):
    return JSONResponse(content=await get_audit_logs(page=page, page_size=page_size))


# ── Feedback ──────────────────────────────────────────────
@router.post("/api/feedback")
async def feedback(request: Request):
    user_id = getattr(request.state, "user_id", "unknown")
    body = await request.json()
    inv = body.get("invoice_id",""); orig = body.get("original_decision",""); corr = body.get("correct_decision","")
    if not all([inv, orig, corr]): raise HTTPException(400, "Missing required fields")
    await write_audit_log({"event_type":"FEEDBACK_SUBMITTED","user_id":user_id,"invoice_id":inv,
        "details":{"original":orig,"corrected":corr,"reason":body.get("reason","")}})
    return JSONResponse(content={"status":"ok","message":"Feedback recorded"})


# ── X-Ray Trace ───────────────────────────────────────────
@router.get("/api/xray/trace/{invoice_id}")
async def xray_trace(invoice_id: str, request: Request):
    import re
    if not re.match(r"^[A-Z0-9\-]{3,50}$", invoice_id.upper()): raise HTTPException(400,"Invalid invoice_id")
    return JSONResponse(content=get_demo_trace_data(invoice_id))


# ── Rate limit stats (admin) ──────────────────────────────
@router.get("/api/rate-limit/stats")
async def rate_stats(request: Request):
    if getattr(request.state, "user_role", "viewer") != "admin": raise HTTPException(403, "Admin only")
    return JSONResponse(content=get_rate_limiter().get_stats())
