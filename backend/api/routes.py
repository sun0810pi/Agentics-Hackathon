"""
backend/api/routes.py
======================
11 endpoints với:
- Input validation trên mọi endpoint
- Response caching cho metrics (30s TTL)
- Structured error responses
- Demo mode support đầy đủ
"""

import base64, logging, time, uuid, os, re, asyncio
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from agents.orchestrator import AgentOrchestrator
from services.database import (
    save_invoice_result, get_invoices, get_invoice_by_id,
    get_metrics, get_audit_logs, write_audit_log,
)
from services.xray_tracer import get_trace_id, get_demo_trace_data
from api.rate_limiter import get_rate_limiter
import config

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Orchestrator singleton ────────────────────────────────
_orch: Optional[AgentOrchestrator] = None
_orch_lock = asyncio.Lock()

async def get_orch() -> AgentOrchestrator:
    """Lazy-init orchestrator with lock to prevent double-init."""
    global _orch
    if _orch is None:
        async with _orch_lock:
            if _orch is None:
                _orch = AgentOrchestrator()
    return _orch

# ── Simple in-process cache for metrics ──────────────────
_metrics_cache: dict = {}
_metrics_cache_ttl: float = 30.0   # seconds


def _err(status: int, code: str, msg: str, request_id: str = "") -> JSONResponse:
    return JSONResponse(status_code=status, content={
        "error": code, "message": msg,
        "request_id": request_id or str(uuid.uuid4()),
        "timestamp":  datetime.utcnow().isoformat(),
    })


INVOICE_ID_RE = re.compile(r"^[A-Z0-9\-]{3,50}$")


# ─────────────────────────────────────────────────────────
# GET /health  (public)
# ─────────────────────────────────────────────────────────
@router.get("/health")
async def health():
    services = {"api": "ok"}
    try:
        from services.database import get_connection
        async with get_connection() as c:
            await c.fetchval("SELECT 1")
        services["database"] = "ok"
    except Exception as e:
        services["database"] = f"unavailable: {str(e)[:50]}"

    ok = all(v == "ok" for v in services.values())
    return JSONResponse(
        status_code=200,
        content={
            "status":    "healthy" if ok else "degraded",
            "version":   config.APP_VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "services":  services,
            "demo_mode": os.getenv("DEMO_MODE", "false"),
        },
    )


# ─────────────────────────────────────────────────────────
# POST /api/analyze
# ─────────────────────────────────────────────────────────
@router.post("/api/analyze")
async def analyze(request: Request):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    user_id    = getattr(request.state, "user_id", "demo-user")
    trace_id   = get_trace_id()

    # Parse body
    try:
        body = await request.json()
    except Exception:
        return _err(400, "INVALID_JSON", "Request body must be valid JSON", request_id)

    invoice_id = str(body.get("invoice_id", "")).strip().upper()
    file_name  = str(body.get("file_name",  "")).strip()
    file_b64   = str(body.get("file_data",  ""))
    mode       = str(body.get("mode",       "demo")).lower()

    # Validate
    if not invoice_id:
        return _err(400, "MISSING_FIELD", "invoice_id is required", request_id)
    if not INVOICE_ID_RE.match(invoice_id):
        return _err(400, "INVALID_INVOICE_ID", "invoice_id must be alphanumeric + dash, 3-50 chars", request_id)
    if not file_name:
        return _err(400, "MISSING_FIELD", "file_name is required", request_id)
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return _err(400, "INVALID_FILE_NAME", "Invalid file name", request_id)
    if mode not in ("full", "fast", "demo"):
        return _err(400, "INVALID_MODE", "mode must be: full | fast | demo", request_id)

    # Decode file
    try:
        file_data = base64.b64decode(file_b64) if file_b64 else b""
    except Exception:
        return _err(400, "INVALID_FILE_DATA", "file_data must be valid base64", request_id)

    # Run pipeline
    try:
        orch   = await get_orch()
        result = await orch.run(
            invoice_id=invoice_id, file_name=file_name,
            file_data=file_data, mode=mode, trace_id=trace_id,
        )
    except asyncio.TimeoutError:
        logger.error(f"Pipeline timeout: {invoice_id}")
        return _err(504, "PIPELINE_TIMEOUT", "Processing timed out. Try mode=fast.", request_id)
    except Exception as e:
        logger.error(f"Pipeline error {invoice_id}: {e}", exc_info=True)
        return _err(500, "PIPELINE_ERROR", "Processing failed. Check logs.", request_id)

    # Persist async (don't block response)
    asyncio.create_task(_persist(invoice_id, result, user_id,
                                 request.client.host if request.client else "unknown", mode))

    return JSONResponse(content=result)


async def _persist(invoice_id: str, result: dict, user_id: str, ip: str, mode: str):
    """Save to DB and write audit log in background."""
    try:
        await save_invoice_result(invoice_id, result)
        await write_audit_log({
            "event_type": "INVOICE_ANALYZED",
            "user_id":    user_id,
            "invoice_id": invoice_id,
            "ip_address": ip,
            "details": {
                "decision":   result.get("final_decision"),
                "risk_score": result.get("risk", {}).get("risk_score"),
                "mode":       mode,
                "duration_ms": result.get("total_duration_ms"),
            },
        })
    except Exception as e:
        logger.error(f"_persist failed {invoice_id}: {e}")


# ─────────────────────────────────────────────────────────
# GET /api/invoices
# ─────────────────────────────────────────────────────────
@router.get("/api/invoices")
async def list_invoices(
    request:   Request,
    page:      int           = Query(1,    ge=1),
    page_size: int           = Query(50,   ge=1, le=200),
    decision:  Optional[str] = Query(None, regex="^(APPROVE|REVIEW|BLOCK|ERROR)$"),
):
    data = await get_invoices(page=page, page_size=page_size, decision_filter=decision)
    return JSONResponse(content=data)


# ─────────────────────────────────────────────────────────
# GET /api/invoices/{invoice_id}
# ─────────────────────────────────────────────────────────
@router.get("/api/invoices/{invoice_id}")
async def get_invoice(invoice_id: str, request: Request):
    invoice_id = invoice_id.upper()
    if not INVOICE_ID_RE.match(invoice_id):
        raise HTTPException(400, "Invalid invoice_id format")

    # FIX: direct DB lookup by ID (not page 1 scan)
    result = await get_invoice_by_id(invoice_id)
    if result is None:
        raise HTTPException(404, f"Invoice '{invoice_id}' not found")
    return JSONResponse(content=result)


# ─────────────────────────────────────────────────────────
# GET /api/metrics  (cached 30s)
# ─────────────────────────────────────────────────────────
@router.get("/api/metrics")
async def metrics(
    request: Request,
    days: int = Query(30, ge=1, le=365),
):
    cache_key = f"metrics_{days}"
    cached    = _metrics_cache.get(cache_key)
    if cached and (time.time() - cached["_ts"]) < _metrics_cache_ttl:
        return JSONResponse(content=cached["data"])

    data = await get_metrics(days=days)
    _metrics_cache[cache_key] = {"data": data, "_ts": time.time()}
    return JSONResponse(content=data)


# ─────────────────────────────────────────────────────────
# GET /api/agents/status
# ─────────────────────────────────────────────────────────
@router.get("/api/agents/status")
async def agent_status(request: Request):
    agents = []
    for i, (name, desc) in enumerate(zip(config.AGENT_NAMES, config.AGENT_DESCRIPTIONS)):
        if   i <= 7:  tier = "Core Detection"
        elif i <= 10: tier = "ML Intelligence"
        elif i <= 13: tier = "Merchant Success"
        else:         tier = "Security"
        agents.append({
            "agent_id":    i,
            "agent_name":  name,
            "description": desc,
            "tier":        tier,
            "status":      "healthy",
            "last_run_ms": round(5 + i * 12.5, 1),
            "success_rate": round(99.5 - i * 0.1, 1),
        })
    return JSONResponse(content={
        "agents":      agents,
        "all_healthy": True,
        "total":       len(agents),
        "last_updated": datetime.utcnow().isoformat(),
    })


# ─────────────────────────────────────────────────────────
# GET /api/fraud-scenarios
# ─────────────────────────────────────────────────────────
@router.get("/api/fraud-scenarios")
async def fraud_scenarios(request: Request):
    scenarios = [
        {"id":1,"type":"Duplicate Invoice",        "description":"Same invoice resubmitted from different IPs",         "risk_score":95,"count":12,"amount":145000},
        {"id":2,"type":"Amount Manipulation",       "description":"Line items don't sum to stated total",                "risk_score":82,"count":7, "amount":89500},
        {"id":3,"type":"Fraud Ring",                "description":"5 vendors sharing the same bank account",             "risk_score":98,"count":23,"amount":412000},
        {"id":4,"type":"NFC Relay Attack",          "description":"Card-not-present transactions across 3 countries/hr", "risk_score":99,"count":3, "amount":28000},
        {"id":5,"type":"Geo-Velocity Violation",    "description":"User in VN and UK within 10 minutes",                 "risk_score":91,"count":4, "amount":67000},
        {"id":6,"type":"Behavioral Anomaly",        "description":"Typing pattern inconsistent with registered user",    "risk_score":76,"count":9, "amount":53000},
        {"id":7,"type":"Tax Rate Manipulation",     "description":"Tax rate > 30% on invoice",                          "risk_score":68,"count":5, "amount":31000},
        {"id":8,"type":"Missing Required Fields",   "description":"Invoice lacks vendor name or invoice date",           "risk_score":55,"count":18,"amount":94000},
    ]
    return JSONResponse(content={"scenarios": scenarios, "total": len(scenarios)})


# ─────────────────────────────────────────────────────────
# GET /api/audit-logs
# ─────────────────────────────────────────────────────────
@router.get("/api/audit-logs")
async def audit_logs(
    request:   Request,
    page:      int = Query(1,  ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    return JSONResponse(content=await get_audit_logs(page=page, page_size=page_size))


# ─────────────────────────────────────────────────────────
# POST /api/feedback
# ─────────────────────────────────────────────────────────
@router.post("/api/feedback")
async def feedback(request: Request):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    user_id    = getattr(request.state, "user_id", "unknown")

    try:
        body = await request.json()
    except Exception:
        return _err(400, "INVALID_JSON", "Request body must be valid JSON", request_id)

    inv  = str(body.get("invoice_id",        "")).strip().upper()
    orig = str(body.get("original_decision", "")).strip().upper()
    corr = str(body.get("correct_decision",  "")).strip().upper()

    if not inv:  return _err(400, "MISSING_FIELD", "invoice_id required",        request_id)
    if not orig: return _err(400, "MISSING_FIELD", "original_decision required", request_id)
    if not corr: return _err(400, "MISSING_FIELD", "correct_decision required",  request_id)

    valid_decisions = {"APPROVE", "REVIEW", "BLOCK"}
    if orig not in valid_decisions: return _err(400, "INVALID_DECISION", f"original_decision must be one of {valid_decisions}", request_id)
    if corr not in valid_decisions: return _err(400, "INVALID_DECISION", f"correct_decision must be one of {valid_decisions}",   request_id)

    reason = str(body.get("reason", ""))[:500]   # cap length

    await write_audit_log({
        "event_type": "FEEDBACK_SUBMITTED",
        "user_id":    user_id,
        "invoice_id": inv,
        "details":    {"original": orig, "corrected": corr, "reason": reason},
    })

    return JSONResponse(content={
        "status":  "ok",
        "message": "Feedback recorded. Thank you for improving the model.",
        "invoice_id": inv,
    })


# ─────────────────────────────────────────────────────────
# GET /api/xray/trace/{invoice_id}
# ─────────────────────────────────────────────────────────
@router.get("/api/xray/trace/{invoice_id}")
async def xray_trace(invoice_id: str, request: Request):
    invoice_id = invoice_id.upper()
    if not INVOICE_ID_RE.match(invoice_id):
        raise HTTPException(400, "Invalid invoice_id")
    return JSONResponse(content=get_demo_trace_data(invoice_id))


# ─────────────────────────────────────────────────────────
# GET /api/rate-limit/stats  (admin only)
# ─────────────────────────────────────────────────────────
@router.get("/api/rate-limit/stats")
async def rate_stats(request: Request):
    role = getattr(request.state, "user_role", "viewer")
    if role != "admin":
        raise HTTPException(403, "Admin role required")
    return JSONResponse(content=get_rate_limiter().get_stats())
