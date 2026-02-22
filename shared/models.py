"""
shared/models.py
================
CRITICAL: This file is the DATA CONTRACT between frontend and backend.
Both sides must use IDENTICAL models. Any change here must be updated on both sides.

AgentFlow Finance Guard - Shared Pydantic Models
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# =====================================================
# ENUMS
# =====================================================

class Decision(str, Enum):
    APPROVE = "APPROVE"
    REVIEW  = "REVIEW"
    BLOCK   = "BLOCK"
    ERROR   = "ERROR"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH     = "HIGH"
    MEDIUM   = "MEDIUM"
    LOW      = "LOW"
    INFO     = "INFO"

class AgentStatus(str, Enum):
    PENDING   = "PENDING"
    RUNNING   = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED    = "FAILED"
    SKIPPED   = "SKIPPED"

class ProcessingMode(str, Enum):
    FULL  = "full"   # All 17 agents
    FAST  = "fast"   # Core agents only (0-7)
    DEMO  = "demo"   # Simulated responses

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    VND = "VND"
    GBP = "GBP"
    JPY = "JPY"


# =====================================================
# REQUEST MODELS (Frontend → Backend)
# =====================================================

class AnalyzeRequest(BaseModel):
    """
    POST /api/analyze
    Frontend sends this to trigger invoice analysis.
    """
    invoice_id: str = Field(..., description="Unique invoice identifier", example="INV-2026-0001")
    file_name: str  = Field(..., description="Original file name", max_length=255)
    file_data: str  = Field(..., description="Base64 encoded file content")
    mode: ProcessingMode = Field(default=ProcessingMode.FULL)
    priority: int = Field(default=5, ge=1, le=10, description="Processing priority 1-10")
    
    @field_validator('invoice_id')
    @classmethod
    def validate_invoice_id(cls, v: str) -> str:
        import re
        if not re.match(r'^[A-Z0-9\-]{3,50}$', v):
            raise ValueError("Invalid invoice ID format")
        return v

    @field_validator('file_name')
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        import re
        # Whitelist: only safe filename chars
        if not re.match(r'^[a-zA-Z0-9._\-\s]{1,255}$', v):
            raise ValueError("Invalid file name")
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError("Path traversal detected")
        allowed_ext = {'.pdf', '.png', '.jpg', '.jpeg'}
        if not any(v.lower().endswith(ext) for ext in allowed_ext):
            raise ValueError("File type not allowed")
        return v


class FeedbackRequest(BaseModel):
    """
    POST /api/feedback
    User provides feedback on agent decision (for continuous learning).
    """
    invoice_id: str
    original_decision: Decision
    correct_decision: Decision
    reason: Optional[str] = Field(None, max_length=500)
    reviewer_id: str


class MetricsRequest(BaseModel):
    """
    GET /api/metrics - query params
    """
    days: int = Field(default=30, ge=1, le=365)
    merchant_id: Optional[str] = None


# =====================================================
# AGENT RESULT MODELS
# =====================================================

class AgentResult(BaseModel):
    """Result from a single agent's execution."""
    agent_id: int
    agent_name: str
    status: AgentStatus
    duration_ms: float
    confidence: float = Field(ge=0.0, le=1.0)
    findings: Dict[str, Any] = Field(default_factory=dict)
    flags: List[str]         = Field(default_factory=list)
    error: Optional[str]     = None

class ExtractedInvoice(BaseModel):
    """Data extracted by Agent 0 (OCR)."""
    invoice_number: Optional[str] = None
    vendor_name: Optional[str]    = None
    vendor_id: Optional[str]      = None
    invoice_date: Optional[str]   = None
    due_date: Optional[str]       = None
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    subtotal: Optional[float]     = None
    tax_amount: Optional[float]   = None
    total_amount: Optional[float] = None
    currency: Currency            = Currency.USD
    po_number: Optional[str]      = None
    ocr_confidence: float         = Field(ge=0.0, le=1.0, default=0.0)

class PIIReport(BaseModel):
    """PII masking report from Agent 1."""
    fields_masked: List[str] = Field(default_factory=list)
    gdpr_compliant: bool     = False
    pii_detected: bool       = False
    masked_data: Dict[str, str] = Field(default_factory=dict)

class RiskAssessment(BaseModel):
    """Risk scoring from Agent 3 (AI Analyst)."""
    risk_score: float = Field(ge=0.0, le=100.0)
    risk_level: Severity
    decision: Decision
    confidence: float = Field(ge=0.0, le=1.0)
    risk_factors: List[str]      = Field(default_factory=list)
    explanation: str             = ""
    bedrock_model: str           = "claude-3-sonnet"

class FraudIndicators(BaseModel):
    """Fraud signals detected across all agents."""
    duplicate_invoice: bool      = False
    amount_mismatch: bool        = False
    suspicious_vendor: bool      = False
    unusual_timing: bool         = False
    geo_velocity_flag: bool      = False
    fraud_ring_member: bool      = False
    behavioral_anomaly: bool     = False
    total_flags: int             = 0
    flag_details: List[str]      = Field(default_factory=list)

class SecurityThreats(BaseModel):
    """Security findings from Tier 4 agents."""
    nfc_relay_detected: bool     = False
    geo_velocity_exceeded: bool  = False
    fraud_ring_detected: bool    = False
    behavioral_inconsistency: bool = False
    threat_level: Severity       = Severity.LOW
    threat_details: List[str]    = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)

class MLInsights(BaseModel):
    """ML analytics from Agent 8."""
    anomaly_score: float         = Field(ge=0.0, le=1.0, default=0.0)
    anomaly_detected: bool       = False
    cluster_id: Optional[int]    = None
    similar_frauds: int          = 0
    trend_direction: str         = "stable"  # up | down | stable
    forecast_risk: float         = Field(ge=0.0, le=1.0, default=0.0)
    feature_importances: Dict[str, float] = Field(default_factory=dict)


# =====================================================
# RESPONSE MODELS (Backend → Frontend)
# =====================================================

class AnalyzeResponse(BaseModel):
    """
    Response from POST /api/analyze
    This is THE most important model - frontend renders everything from this.
    """
    # Identifiers
    invoice_id: str
    trace_id: str          # AWS X-Ray trace ID
    request_id: str        # Unique request ID
    
    # Timing
    started_at: datetime
    completed_at: datetime
    total_duration_ms: float
    
    # Processing
    mode: ProcessingMode
    agents_run: int
    agents_succeeded: int
    agents_failed: int
    
    # Core Results
    extracted: ExtractedInvoice
    pii_report: PIIReport
    risk: RiskAssessment
    fraud_indicators: FraudIndicators
    security: SecurityThreats
    ml_insights: MLInsights
    
    # Final Decision
    final_decision: Decision
    final_confidence: float = Field(ge=0.0, le=1.0)
    
    # Agent-level results (for Observability page)
    agent_results: List[AgentResult] = Field(default_factory=list)
    
    # Audit
    audit_hash: str        # SHA-256 of full result (immutable audit trail)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class InvoiceListResponse(BaseModel):
    """Response from GET /api/invoices"""
    invoices: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    has_more: bool


class MetricsResponse(BaseModel):
    """Response from GET /api/metrics"""
    # Summary KPIs
    total_processed: int
    total_approved: int
    total_blocked: int
    total_review: int
    
    accuracy_rate: float
    automation_rate: float
    avg_processing_time_ms: float
    
    # Financial
    total_amount_processed: float
    total_fraud_prevented: float
    annual_value_delivered: float
    
    # Trends (last N days, one entry per day)
    daily_volume: List[Dict[str, Any]]       # [{date, count, amount}]
    risk_distribution: List[Dict[str, Any]]   # [{risk_level, count, pct}]
    agent_performance: List[Dict[str, Any]]   # [{agent_id, avg_ms, success_rate}]
    fraud_by_type: List[Dict[str, Any]]       # [{type, count}]
    
    # Top merchants
    top_merchants: List[Dict[str, Any]]       # [{merchant, volume, risk_avg}]


class AgentStatusResponse(BaseModel):
    """Response from GET /api/agents/status"""
    agents: List[Dict[str, Any]]
    all_healthy: bool
    last_updated: datetime


class FraudScenarioResponse(BaseModel):
    """
    Response from GET /api/fraud-scenarios
    Used by Fraud Detection page to show real fraud patterns.
    """
    scenarios: List[Dict[str, Any]]
    total: int


class AuditLogResponse(BaseModel):
    """Response from GET /api/audit-logs"""
    logs: List[Dict[str, Any]]
    total: int
    page: int


class HealthResponse(BaseModel):
    """Response from GET /health"""
    status: str          # "healthy" | "degraded" | "unhealthy"
    version: str
    timestamp: datetime
    services: Dict[str, str]   # {service_name: "ok" | "error"}
    uptime_seconds: float


class ErrorResponse(BaseModel):
    """Standard error response for all 4xx/5xx errors."""
    error: str
    message: str
    request_id: str
    timestamp: datetime
    trace_id: Optional[str] = None


# =====================================================
# RATE LIMITING MODELS
# =====================================================

class RateLimitInfo(BaseModel):
    """Added to response headers for rate limit transparency."""
    limit: int
    remaining: int
    reset_at: datetime
    user_id: str
