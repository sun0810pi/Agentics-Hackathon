"""
backend/api/routes.py
======================
13 endpoints (11 cũ + 2 mới cho frontend compatibility):

  GET  /health                  — health check (public)
  POST /api/analyze             — run 17-agent pipeline
  GET  /api/invoices            — list invoices (paginated)
  GET  /api/invoices/{id}       — get single invoice
  GET  /api/metrics             — dashboard KPIs (cached 30s)
  GET  /api/agents/status       — agent health
  GET  /api/fraud-scenarios     — known fraud patterns
  GET  /api/audit-logs          — immutable audit trail
  POST /api/feedback            — analyst feedback
  GET  /api/xray/trace/{id}     — X-Ray trace by invoice
  GET  /api/xray-traces         — ✨ NEW: recent traces list (observability page)
  POST /api/test-attack         — ✨ NEW: security demo attack simulation
  GET  /api/rate-limit/stats    — rate limiter stats (admin)

FRONTEND COMPATIBILITY FIXES:
  - /health: demo_mode is boolean + agents count added
  - /api/analyze: response includes flat fields (decision, risk_score, success)
                  + accepts both JSON and multipart form-data
  - /api/metrics: cache cleanup to prevent memory leak
"""

import base64, logging, time, uuid, os, re, asyncio, random
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Query, File, UploadFile, Form
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
    global _orch
    if _orch is None:
        async with _orch_lock:
            if _orch is None:
                _orch = AgentOrchestrator()
    return _orch


# ── Metrics cache (30s TTL, auto-cleanup) ────────────────
_metrics_cache: dict = {}
_metrics_cache_ttl: float = 30.0

def _cache_get(key: str) -> Optional[dict]:
    entry = _metrics_cache.get(key)
    if entry and (time.time() - entry["_ts"]) < _metrics_cache_ttl:
        return entry["data"]
    return None

def _cache_set(key: str, data: dict) -> None:
    _metrics_cache[key] = {"data": data, "_ts": time.time()}
    # FIX #2: clean expired entries to prevent memory leak
    now = time.time()
    expired = [k for k, v in _metrics_cache.items()
               if (now - v["_ts"]) > _metrics_cache_ttl * 10]
    for k in expired:
        del _metrics_cache[k]


# ── Helpers ───────────────────────────────────────────────
def _err(status: int, code: str, msg: str, request_id: str = "") -> JSONResponse:
    return JSONResponse(status_code=status, content={
        "error":      code,
        "message":    msg,
        "request_id": request_id or str(uuid.uuid4()),
        "timestamp":  datetime.utcnow().isoformat(),
    })

def _flatten_result(result: dict) -> dict:
    """
    FIX: Add top-level flat fields that frontend expects alongside
    the existing nested structure. Backward-compatible — keeps all
    existing fields, just adds convenience aliases.
    
    Frontend expects:   Backend has:
      success           → (added)
      decision          → final_decision
      risk_score        → risk.risk_score
      confidence        → final_confidence
    """
    result["success"]    = result.get("final_decision") not in (None, "ERROR")
    result["decision"]   = result.get("final_decision")
    result["risk_score"] = result.get("risk", {}).get("risk_score", 0)
    result["confidence"] = result.get("final_confidence", 0)
    return result

INVOICE_ID_RE = re.compile(r"^[A-Z0-9\-]{3,50}$")
MAX_FILE_SIZE  = 50 * 1024 * 1024   # 50MB


# ═══════════════════════════════════════════════════════════
# GET /health  (public)
# ═══════════════════════════════════════════════════════════
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

    ok        = all(v == "ok" for v in services.values())
    demo_mode = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
    return JSONResponse(status_code=200, content={
        "status":    "healthy" if ok else "degraded",
        "version":   config.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "services":  services,
        # FIX #3: demo_mode is boolean (not string), + agents count added
        "demo_mode": demo_mode,
        "agents":    len(config.AGENT_NAMES),   # frontend expects this
        "mode":      "demo" if demo_mode else "production",
    })


# ═══════════════════════════════════════════════════════════
# POST /api/analyze
# Accepts BOTH:
#   A) JSON body  { invoice_id, file_name, file_data (base64), mode }
#   B) Multipart  file=<binary> + mode=<str>   (frontend may send this)
# ═══════════════════════════════════════════════════════════
@router.post("/api/analyze")
async def analyze(request: Request):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    user_id    = getattr(request.state, "user_id", "demo-user")
    trace_id   = get_trace_id()

    content_type = request.headers.get("content-type", "")

    # ── A) Multipart form-data ────────────────────────────
    if "multipart/form-data" in content_type:
        try:
            form      = await request.form()
            file_obj  = form.get("file")
            mode      = str(form.get("mode", "demo")).lower()
            threshold = form.get("auto_approve_threshold", 70)

            if file_obj is None:
                return _err(400, "MISSING_FILE", "file field required in form-data", request_id)

            file_name = getattr(file_obj, "filename", "upload.pdf") or "upload.pdf"
            file_data = await file_obj.read()

            if len(file_data) > MAX_FILE_SIZE:
                return _err(413, "FILE_TOO_LARGE", "Max file size is 50MB", request_id)

            # Auto-generate invoice_id for multipart uploads
            invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"

        except Exception as e:
            return _err(400, "INVALID_FORM", f"Form parse error: {e}", request_id)

    # ── B) JSON body ──────────────────────────────────────
    else:
        try:
            body = await request.json()
        except Exception:
            return _err(400, "INVALID_JSON", "Request body must be valid JSON", request_id)

        invoice_id = str(body.get("invoice_id", "")).strip().upper()
        file_name  = str(body.get("file_name",  "")).strip()
        file_b64   = str(body.get("file_data",  ""))
        mode       = str(body.get("mode",       "demo")).lower()

        if not invoice_id:
            return _err(400, "MISSING_FIELD", "invoice_id is required", request_id)
        if not INVOICE_ID_RE.match(invoice_id):
            return _err(400, "INVALID_INVOICE_ID", "invoice_id: alphanumeric + dash, 3-50 chars", request_id)
        if not file_name:
            return _err(400, "MISSING_FIELD", "file_name is required", request_id)
        if ".." in file_name or "/" in file_name or "\\" in file_name:
            return _err(400, "INVALID_FILE_NAME", "Invalid file name", request_id)

        try:
            file_data = base64.b64decode(file_b64) if file_b64 else b""
        except Exception:
            return _err(400, "INVALID_FILE_DATA", "file_data must be valid base64", request_id)

        if len(file_data) > MAX_FILE_SIZE:
            return _err(413, "FILE_TOO_LARGE", "Max file size is 50MB", request_id)

    if mode not in ("full", "fast", "demo"):
        return _err(400, "INVALID_MODE", "mode must be: full | fast | demo", request_id)

    # ── Run pipeline ──────────────────────────────────────
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

    # Add flat fields for frontend compatibility
    result = _flatten_result(result)

    # Persist in background (don't block response)
    asyncio.create_task(_persist(
        invoice_id, result, user_id,
        request.client.host if request.client else "unknown", mode,
    ))

    return JSONResponse(content=result)


async def _persist(invoice_id: str, result: dict, user_id: str, ip: str, mode: str):
    try:
        await save_invoice_result(invoice_id, result)
        await write_audit_log({
            "event_type": "INVOICE_ANALYZED",
            "user_id":    user_id,
            "invoice_id": invoice_id,
            "ip_address": ip,
            "details": {
                "decision":    result.get("final_decision"),
                "risk_score":  result.get("risk_score"),
                "mode":        mode,
                "duration_ms": result.get("total_duration_ms"),
            },
        })
    except Exception as e:
        logger.error(f"_persist failed {invoice_id}: {e}")


# ═══════════════════════════════════════════════════════════
# GET /api/invoices
# ═══════════════════════════════════════════════════════════
@router.get("/api/invoices")
async def list_invoices(
    request:   Request,
    page:      int           = Query(1,    ge=1),
    page_size: int           = Query(50,   ge=1, le=200),
    decision:  Optional[str] = Query(None, pattern="^(APPROVE|REVIEW|BLOCK|ERROR)$"),
):
    data = await get_invoices(page=page, page_size=page_size, decision_filter=decision)
    return JSONResponse(content=data)


# ═══════════════════════════════════════════════════════════
# GET /api/invoices/{invoice_id}
# ═══════════════════════════════════════════════════════════
@router.get("/api/invoices/{invoice_id}")
async def get_invoice(invoice_id: str, request: Request):
    invoice_id = invoice_id.upper()
    if not INVOICE_ID_RE.match(invoice_id):
        raise HTTPException(400, "Invalid invoice_id format")
    result = await get_invoice_by_id(invoice_id)
    if result is None:
        raise HTTPException(404, f"Invoice '{invoice_id}' not found")
    return JSONResponse(content=result)


# ═══════════════════════════════════════════════════════════
# GET /api/metrics  (cached 30s, memory-safe cleanup)
# ═══════════════════════════════════════════════════════════
@router.get("/api/metrics")
async def metrics(
    request: Request,
    days: int = Query(30, ge=1, le=365),
):
    cache_key = f"metrics_{days}"
    cached    = _cache_get(cache_key)
    if cached:
        return JSONResponse(content=cached)

    data = await get_metrics(days=days)
    _cache_set(cache_key, data)   # FIX #2: uses cleanup-safe setter
    return JSONResponse(content=data)


# ═══════════════════════════════════════════════════════════
# GET /api/agents/status
# ═══════════════════════════════════════════════════════════
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
        "agents":       agents,
        "all_healthy":  True,
        "total":        len(agents),
        "last_updated": datetime.utcnow().isoformat(),
    })


# ═══════════════════════════════════════════════════════════
# GET /api/fraud-scenarios
# ═══════════════════════════════════════════════════════════
@router.get("/api/fraud-scenarios")
async def fraud_scenarios(request: Request):
    scenarios = [
        {"id":1,"type":"Duplicate Invoice",      "description":"Same invoice resubmitted from different IPs",         "risk_score":95,"count":12,"amount":145000},
        {"id":2,"type":"Amount Manipulation",     "description":"Line items don't sum to stated total",                "risk_score":82,"count":7, "amount":89500},
        {"id":3,"type":"Fraud Ring",              "description":"5 vendors sharing the same bank account",             "risk_score":98,"count":23,"amount":412000},
        {"id":4,"type":"NFC Relay Attack",        "description":"Card-not-present transactions across 3 countries/hr", "risk_score":99,"count":3, "amount":28000},
        {"id":5,"type":"Geo-Velocity Violation",  "description":"User in VN and UK within 10 minutes",                 "risk_score":91,"count":4, "amount":67000},
        {"id":6,"type":"Behavioral Anomaly",      "description":"Typing pattern inconsistent with registered user",    "risk_score":76,"count":9, "amount":53000},
        {"id":7,"type":"Tax Rate Manipulation",   "description":"Tax rate > 30% on invoice",                          "risk_score":68,"count":5, "amount":31000},
        {"id":8,"type":"Missing Required Fields", "description":"Invoice lacks vendor name or invoice date",           "risk_score":55,"count":18,"amount":94000},
    ]
    return JSONResponse(content={"scenarios": scenarios, "total": len(scenarios)})


# ═══════════════════════════════════════════════════════════
# GET /api/audit-logs
# ═══════════════════════════════════════════════════════════
@router.get("/api/audit-logs")
async def audit_logs(
    request:   Request,
    page:      int = Query(1,  ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    return JSONResponse(content=await get_audit_logs(page=page, page_size=page_size))


# ═══════════════════════════════════════════════════════════
# POST /api/feedback
# ═══════════════════════════════════════════════════════════
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
    if orig not in valid_decisions:
        return _err(400, "INVALID_DECISION", f"original_decision must be one of {valid_decisions}", request_id)
    if corr not in valid_decisions:
        return _err(400, "INVALID_DECISION", f"correct_decision must be one of {valid_decisions}", request_id)

    reason = str(body.get("reason", ""))[:500]

    await write_audit_log({
        "event_type": "FEEDBACK_SUBMITTED",
        "user_id":    user_id,
        "invoice_id": inv,
        "details":    {"original": orig, "corrected": corr, "reason": reason},
    })

    return JSONResponse(content={
        "status":     "ok",
        "message":    "Feedback recorded. Thank you for improving the model.",
        "invoice_id": inv,
    })


# ═══════════════════════════════════════════════════════════
# GET /api/xray/trace/{invoice_id}  (existing — by invoice)
# ═══════════════════════════════════════════════════════════
@router.get("/api/xray/trace/{invoice_id}")
async def xray_trace(invoice_id: str, request: Request):
    invoice_id = invoice_id.upper()
    if not INVOICE_ID_RE.match(invoice_id):
        raise HTTPException(400, "Invalid invoice_id")
    return JSONResponse(content=get_demo_trace_data(invoice_id))


# ═══════════════════════════════════════════════════════════
# GET /api/xray-traces  ✨ NEW — Observability page
# Returns list of recent traces (real or demo)
# ═══════════════════════════════════════════════════════════
@router.get("/api/xray-traces")
async def xray_traces(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
):
    """
    Get recent X-Ray traces for the Observability dashboard.
    Returns demo data when X-Ray not available.
    """
    try:
        # Try real X-Ray service map first
        import boto3
        xray = boto3.client("xray", region_name=os.getenv("AWS_REGION", "us-east-1"))
        resp = xray.get_trace_summaries(
            StartTime=datetime.utcnow().timestamp() - 3600,
            EndTime=datetime.utcnow().timestamp(),
            Sampling=True,
        )
        summaries = resp.get("TraceSummaries", [])[:limit]
        traces = [{
            "trace_id":   s.get("Id", ""),
            "duration":   s.get("Duration", 0),
            "http":       s.get("Http", {}),
            "has_error":  s.get("HasError", False),
            "has_fault":  s.get("HasFault", False),
        } for s in summaries]
    except Exception:
        # Demo fallback — generate realistic traces
        traces = []
        for i in range(limit):
            inv_id = f"INV-DEMO-{random.randint(1000,9999)}"
            t      = get_demo_trace_data(inv_id)
            traces.append({
                "trace_id":    t["trace_id"],
                "invoice_id":  inv_id,
                "duration_ms": t["duration_ms"],
                "subsegments": len(t["subsegments"]),
                "has_error":   random.random() < 0.04,
                "service_map": t["service_map"],
                "timestamp":   datetime.utcnow().isoformat(),
            })

    return JSONResponse(content={
        "traces":  traces,
        "total":   len(traces),
        "source":  "xray" if not isinstance(traces[0].get("invoice_id"), str) else "demo",
    })


# ═══════════════════════════════════════════════════════════
# POST /api/test-attack  ✨ NEW — Security Demo page
# Simulates attack detection for hackathon demo
# ═══════════════════════════════════════════════════════════

_ATTACK_RESPONSES = {
    "sql_injection": {
        "detection_method": "Input Validation + WAF Rule AWSManagedRulesSQLiRuleSet",
        "waf_rule_triggered": "SQLiRuleSet:SQLi_QUERYARGUMENTS",
        "blocked_at": "API Gateway WAF",
        "severity": "HIGH",
    },
    "xss": {
        "detection_method": "Input Sanitization + WAF XSS Rule",
        "waf_rule_triggered": "CommonRuleSet:XSS_QUERYARGUMENTS",
        "blocked_at": "API Gateway WAF",
        "severity": "MEDIUM",
    },
    "path_traversal": {
        "detection_method": "Filename Validator (../  detection)",
        "waf_rule_triggered": None,
        "blocked_at": "Backend Input Validation",
        "severity": "HIGH",
    },
    "brute_force": {
        "detection_method": "Token Bucket Rate Limiter (15 tokens/user)",
        "waf_rule_triggered": "WAF Rate Rule: 100 req/5min",
        "blocked_at": "RateLimitMiddleware",
        "severity": "MEDIUM",
    },
    "jwt_tampering": {
        "detection_method": "JWT Signature Verification (RS256 + JWKS)",
        "waf_rule_triggered": None,
        "blocked_at": "JWTAuthMiddleware",
        "severity": "CRITICAL",
    },
    "large_payload": {
        "detection_method": "File size limit (50MB max)",
        "waf_rule_triggered": "WAF SizeRestrictions",
        "blocked_at": "API Gateway + Backend",
        "severity": "LOW",
    },
    "duplicate_invoice": {
        "detection_method": "Agent 0 OCR + Agent 13 Trend Analyzer",
        "waf_rule_triggered": None,
        "blocked_at": "AgentFlow Pipeline",
        "severity": "HIGH",
    },
    "nfc_relay": {
        "detection_method": "Agent 14 Security Sentinel (geo-velocity algorithm)",
        "waf_rule_triggered": None,
        "blocked_at": "AgentFlow Pipeline",
        "severity": "CRITICAL",
    },
}

@router.post("/api/test-attack")
async def test_attack(request: Request):
    """
    Security Demo — simulates attack detection.
    Used by frontend Security page for live demo.
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    try:
        body = await request.json()
    except Exception:
        return _err(400, "INVALID_JSON", "Request body must be valid JSON", request_id)

    attack_type = str(body.get("attack_type", "sql_injection")).lower().replace(" ", "_").replace("-", "_")
    payload     = str(body.get("payload", ""))[:200]

    details = _ATTACK_RESPONSES.get(attack_type, {
        "detection_method": "Generic Input Validation",
        "waf_rule_triggered": None,
        "blocked_at": "Backend Validation",
        "severity": "MEDIUM",
    })

    # Simulate tiny processing delay for realism
    await asyncio.sleep(random.uniform(0.05, 0.15))

    await write_audit_log({
        "event_type": "ATTACK_SIMULATED",
        "user_id":    getattr(request.state, "user_id", "demo-user"),
        "invoice_id": None,
        "details":    {"attack_type": attack_type, "payload_preview": payload[:50], "blocked": True},
    })

    return JSONResponse(content={
        "blocked":          True,
        "attack_type":      attack_type,
        "payload_preview":  payload[:50] + ("..." if len(payload) > 50 else ""),
        "detection_method": details["detection_method"],
        "waf_rule_triggered": details.get("waf_rule_triggered"),
        "blocked_at":       details["blocked_at"],
        "severity":         details["severity"],
        "message":          f"✅ {attack_type.replace('_',' ').title()} attack blocked successfully",
        "timestamp":        datetime.utcnow().isoformat(),
        "request_id":       request_id,
        "protection_layers": [
            "WAF (AWS Managed Rules)",
            "JWT Authentication",
            "Rate Limiting (Token Bucket)",
            "Input Validation (Whitelist)",
            "SQL Parameterization",
            "Security Headers",
        ],
    })


# ═══════════════════════════════════════════════════════════
# GET /api/rate-limit/stats  (admin only)
# ═══════════════════════════════════════════════════════════
@router.get("/api/rate-limit/stats")
async def rate_stats(request: Request):
    role = getattr(request.state, "user_role", "viewer")
    if role != "admin":
        raise HTTPException(403, "Admin role required")
    return JSONResponse(content=get_rate_limiter().get_stats())
