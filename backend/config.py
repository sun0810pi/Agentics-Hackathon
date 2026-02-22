"""
backend/config.py
==================
Backend configuration — mirrors frontend/config.py structure
but reads from environment variables / AWS Secrets Manager.
"""

import os

# Agent metadata (must match frontend/config.py exactly)
AGENT_NAMES = [
    "OCR Extractor",           # 0
    "PII Preprocessor",        # 1
    "Decimal Matcher",         # 2
    "AI Analyst",              # 3
    "Audit Seal",              # 4
    "Notifier",                # 5
    "Dashboard Data",          # 6
    "Integrator",              # 7
    "ML Insights",             # 8
    "Continuous Learning",     # 9
    "Multi-Currency",          # 10
    "Merchant Advisor",        # 11
    "Quality Inspector",       # 12
    "Trend Analyzer",          # 13
    "Security Sentinel",       # 14
    "Fraud Ring Analyzer",     # 15
    "Behavioral Consistency",  # 16
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

# Runtime config from env
AWS_REGION           = os.getenv("AWS_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "")
COGNITO_CLIENT_ID    = os.getenv("COGNITO_CLIENT_ID", "")
DB_SECRET_NAME       = os.getenv("DB_SECRET_NAME", "")
SNS_ALERT_TOPIC_ARN  = os.getenv("SNS_ALERT_TOPIC_ARN", "")
ALLOWED_ORIGINS      = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501")
DEBUG                = os.getenv("DEBUG", "false").lower() == "true"
