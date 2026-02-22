"""
shared/constants.py
====================
Constants shared by both frontend and backend.
"""

# App
APP_NAME    = "AgentFlow Finance Guard"
APP_VERSION = "3.1.0"

# Agent info (17 agents total)
AGENT_NAMES = [
    "OCR Extractor",         # 0
    "PII Preprocessor",      # 1
    "Decimal Matcher",       # 2
    "AI Analyst",            # 3
    "Audit Seal",            # 4
    "Notifier",              # 5
    "Dashboard Data",        # 6
    "Integrator",            # 7
    "ML Insights",           # 8
    "Continuous Learning",   # 9
    "Multi-Currency",        # 10
    "Merchant Advisor",      # 11
    "Quality Inspector",     # 12
    "Trend Analyzer",        # 13
    "Security Sentinel",     # 14
    "Fraud Ring Analyzer",   # 15
    "Behavioral Consistency",# 16
]

AGENT_TIERS = {
    "Core Detection":  list(range(0, 8)),
    "ML Intelligence": list(range(8, 11)),
    "Merchant Success":list(range(11, 14)),
    "Security":        list(range(14, 17)),
}

# Risk thresholds
RISK_LOW    = 30
RISK_MEDIUM = 70

# Rate limiting
RATE_LIMIT_MAX_TOKENS  = 15
RATE_LIMIT_REFILL_RATE = 10 / 60  # 10 per minute

# File upload
MAX_FILE_SIZE_MB   = 50
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

# API endpoints
ENDPOINT_HEALTH          = "/health"
ENDPOINT_ANALYZE         = "/api/analyze"
ENDPOINT_METRICS         = "/api/metrics"
ENDPOINT_AGENTS          = "/api/agents/status"
ENDPOINT_INVOICES        = "/api/invoices"
ENDPOINT_FRAUD_SCENARIOS = "/api/fraud-scenarios"
ENDPOINT_AUDIT_LOGS      = "/api/audit-logs"
ENDPOINT_FEEDBACK        = "/api/feedback"
ENDPOINT_XRAY            = "/api/xray/trace"
