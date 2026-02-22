"""backend/config.py — Backend configuration from env vars."""
import os

AWS_REGION           = os.getenv("AWS_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "")
COGNITO_CLIENT_ID    = os.getenv("COGNITO_CLIENT_ID", "")
DB_SECRET_NAME       = os.getenv("DB_SECRET_NAME", "")
DB_HOST              = os.getenv("DB_HOST", "localhost")
DB_PORT              = int(os.getenv("DB_PORT", "5432"))
DB_NAME              = os.getenv("DB_NAME", "agentflow")
DB_USER              = os.getenv("DB_USER", "postgres")
DB_PASSWORD          = os.getenv("DB_PASSWORD", "")
SNS_ALERT_TOPIC_ARN  = os.getenv("SNS_ALERT_TOPIC_ARN", "")
ALLOWED_ORIGINS      = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501")
DEBUG                = os.getenv("DEBUG", "false").lower() == "true"
APP_VERSION          = "3.1.0"

# Agent metadata — must match shared/constants.py
AGENT_NAMES = [
    "OCR Extractor", "PII Preprocessor", "Decimal Matcher", "AI Analyst",
    "Audit Seal", "Notifier", "Dashboard Data", "Integrator",
    "ML Insights", "Continuous Learning", "Multi-Currency",
    "Merchant Advisor", "Quality Inspector", "Trend Analyzer",
    "Security Sentinel", "Fraud Ring Analyzer", "Behavioral Consistency",
]

AGENT_DESCRIPTIONS = [
    "Extracts invoice data using AWS Textract OCR",
    "Masks PII for GDPR compliance",
    "Compares invoice amounts with PO data",
    "AI-powered fraud risk scoring with Bedrock Claude",
    "Creates immutable audit trail with cryptographic seal",
    "Sends alerts via Slack, email, SMS",
    "Aggregates metrics for dashboard",
    "Syncs with external systems (ERP, Sheets)",
    "ML-based anomaly detection and forecasting",
    "Continuous learning from feedback loop",
    "Handles multi-currency conversion and FX risk",
    "Provides merchant optimization recommendations",
    "Validates extraction quality and completeness",
    "Analyzes trends and patterns over time",
    "Detects security threats (NFC relay, geo-velocity)",
    "Identifies coordinated fraud rings via graph analysis",
    "Validates user behavior consistency",
]
