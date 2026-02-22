"""
shared/models.py
================
DATA CONTRACT giữa frontend và backend.
Cả 2 bên PHẢI dùng CHÍNH XÁC models này.
Bất kỳ thay đổi nào phải cập nhật cả 2 bên.
"""

from pydantic import BaseModel, Field, field_validator
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
    FULL = "full"
    FAST = "fast"
    DEMO = "demo"

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
    """POST /api/analyze"""
    invoice_id: str = Field(..., max_length=50, example="INV-2026-0001")
    file_name:  str = Field(..., max_length=255)
    file_data:  str = Field(..., description="Base64 encoded file")
    mode: ProcessingMode = ProcessingMode.FULL
    priority: int = Field(default=5, ge=1, le=10)

    @field_validator("invoice_id")
    @classmethod
    def validate_invoice_id(cls, v: str) -> str:
        import re
        if not re.match(r"^[A-Z0-9\-]{3,50}$", v):
            raise ValueError("Invalid invoice_id format")
        return v

    @field_validator("file_name")
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        if ".." in v or "/" in v or "\\" in v:
            raise ValueError("Path traversal detected")
        allowed = {".pdf", ".png", ".jpg", ".jpeg"}
        if not any(v.lower().endswith(ext) for ext in allowed):
            raise ValueError("File type not allowed")
        return v


class FeedbackRequest(BaseModel):
    """POST /api/feedback"""
    invoice_id:        str
    original_decision: Decision
    correct_decision:  Decision
    reason:            Optional[str] = Field(None, max_length=500)
    reviewer_id:       str


# =====================================================
# RESPONSE MODELS (Backend → Frontend)
# =====================================================

class AgentResult(BaseModel):
    agent_id:    int
    agent_name:  str
    status:      AgentStatus
    duration_ms: float
    confidence:  float = Field(ge=0.0, le=1.0)
    findings:    Dict[str, Any] = Field(default_factory=dict)
    flags:       List[str]      = Field(default_factory=list)
    error:       Optional[str]  = None


class AnalyzeResponse(BaseModel):
    """Response from POST /api/analyze — the most important model"""
    invoice_id:        str
    trace_id:          str
    request_id:        str
    started_at:        str
    completed_at:      str
    total_duration_ms: float
    mode:              str
    agents_run:        int
    agents_succeeded:  int
    agents_failed:     int
    extracted:         Dict[str, Any]
    pii_report:        Dict[str, Any]
    risk:              Dict[str, Any]
    fraud_indicators:  Dict[str, Any]
    security:          Dict[str, Any]
    ml_insights:       Dict[str, Any]
    final_decision:    str
    final_confidence:  float
    agent_results:     List[Dict[str, Any]] = Field(default_factory=list)
    audit_hash:        str


class MetricsResponse(BaseModel):
    total_processed:          int
    total_approved:           int
    total_blocked:            int
    total_review:             int
    accuracy_rate:            float
    automation_rate:          float
    avg_processing_time_ms:   float
    total_amount_processed:   float
    total_fraud_prevented:    float
    annual_value_delivered:   float
    daily_volume:             List[Dict[str, Any]]
    risk_distribution:        List[Dict[str, Any]]
    agent_performance:        List[Dict[str, Any]]
    fraud_by_type:            List[Dict[str, Any]]
    top_merchants:            List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status:          str
    version:         str
    timestamp:       str
    services:        Dict[str, str]
    uptime_seconds:  float


class ErrorResponse(BaseModel):
    error:      str
    message:    str
    request_id: str
    timestamp:  str
    trace_id:   Optional[str] = None
