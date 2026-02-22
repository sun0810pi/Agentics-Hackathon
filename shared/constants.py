# =====================================================
# shared/constants.py
# Constants shared between frontend AND backend
# MUST be identical on both sides
# =====================================================

# API version
API_VERSION = "v1"

# Agent tier names
TIER_CORE = "Core Detection"
TIER_INTELLIGENCE = "ML Intelligence"
TIER_MERCHANT = "Merchant Success"
TIER_SECURITY = "Security"

# All 17 agent names (index = agent_id)
AGENT_NAMES = [
    "OCR Extractor",           # 0 - Textract
    "PII Preprocessor",        # 1 - GDPR masking
    "Decimal Matcher",         # 2 - Amount validation
    "AI Analyst",              # 3 - Bedrock risk scoring
    "Audit Seal",              # 4 - Cryptographic audit
    "Notifier",                # 5 - Slack/Email/SMS
    "Dashboard Data",          # 6 - Metrics aggregation
    "Integrator",              # 7 - ERP/Sheets sync
    "ML Insights",             # 8 - Anomaly detection
    "Continuous Learning",     # 9 - Feedback loop
    "Multi-Currency",          # 10 - FX conversion
    "Merchant Advisor",        # 11 - Recommendations
    "Quality Inspector",       # 12 - Extraction QA
    "Trend Analyzer",          # 13 - Pattern analysis
    "Security Sentinel",       # 14 - Threat detection
    "Fraud Ring Analyzer",     # 15 - Graph analysis
    "Behavioral Consistency",  # 16 - User behavior
]

AGENT_TIERS = {
    TIER_CORE: list(range(0, 8)),          # Agents 0-7
    TIER_INTELLIGENCE: list(range(8, 11)), # Agents 8-10
    TIER_MERCHANT: list(range(11, 14)),    # Agents 11-13
    TIER_SECURITY: list(range(14, 17)),    # Agents 14-16
}

# Risk thresholds (must match frontend config.py)
RISK_LOW_THRESHOLD = 30
RISK_MEDIUM_THRESHOLD = 70

# Rate limiting (must match frontend config.py)
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60

# File constraints
MAX_FILE_SIZE_MB = 50
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "image/png",
    "image/jpeg",
]
