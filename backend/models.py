"""
Pydantic Models cho Audit System
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class InvoiceInput(BaseModel):
    """Input từ Excel/Upload"""
    invoice_amount: float = Field(..., description="Số tiền Invoice")
    po_amount: float = Field(..., description="Số tiền PO")
    supplier: str = Field(..., description="Tên nhà cung cấp")
    email: Optional[str] = Field(None, description="Email liên hệ")
    bank_account: Optional[str] = Field(None, description="Số tài khoản")

class Agent1Output(BaseModel):
    """Output từ Agent 1 - Ingestion"""
    transaction_id: str
    invoice_amount: float
    po_amount: float
    supplier: str
    email_masked: str
    bank_account_masked: str
    timestamp: datetime
    status: Literal["validated", "rejected"] = "validated"

class Agent2Output(BaseModel):
    """Output từ Agent 2 - Matching"""
    transaction_id: str
    diff_amount: float
    diff_percentage: float
    match_status: Literal["MATCH", "MISMATCH"]
    threshold_exceeded: bool
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]

class Agent3Output(BaseModel):
    """Output từ Agent 3 - AI Analysis"""
    transaction_id: str
    ai_verdict: str
    confidence_score: float
    recommendations: List[str]
    requires_human_review: bool

class TransactionRecord(BaseModel):
    """Record đầy đủ trong Database"""
    transaction_id: str
    supplier: str
    invoice_amount: float
    po_amount: float
    diff_amount: float
    diff_percentage: float
    match_status: str
    risk_level: str
    ai_verdict: Optional[str] = None
    confidence_score: Optional[float] = None
    requires_human_review: bool = False
    created_at: datetime
    updated_at: datetime
    status: Literal["pending", "approved", "rejected", "manual_review"] = "pending"

class BatchProcessRequest(BaseModel):
    """Request để xử lý batch"""
    items: List[InvoiceInput]

class BatchProcessResponse(BaseModel):
    """Response sau khi xử lý batch"""
    total_processed: int
    success_count: int
    failed_count: int
    results: List[TransactionRecord]

class DashboardStats(BaseModel):
    """Thống kê Dashboard"""
    total_transactions: int
    pending_review: int
    approved: int
    rejected: int
    total_amount: float
    avg_processing_time: float
    high_risk_count: int

class IntegrationConfig(BaseModel):
    """Cấu hình Slack/Telegram/Zalo"""
    type: Literal["slack", "telegram", "zalo"]
    enabled: bool
    webhook_url: Optional[str] = None
    token: Optional[str] = None
    chat_id: Optional[str] = None
