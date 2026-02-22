# AgentFlow Backend

FastAPI + AWS Lambda | 17-Agent Fraud Detection Pipeline

## Chạy local (không cần AWS)

```bash
cd backend
pip install fastapi uvicorn pydantic
uvicorn main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Cấu trúc files

```
backend/
├── main.py                      # FastAPI app factory + middleware stack
├── lambda_handler.py            # AWS Lambda entry point (1 dòng)
├── config.py                    # Env vars + agent metadata
├── Dockerfile                   # Lambda container image
├── requirements.txt
│
├── agents/
│   ├── base.py                  # BaseAgent + AgentContext
│   ├── orchestrator.py          # Tier1 sequential → Tier2/3/4 parallel
│   ├── tier1_core/              # Agents 0-7
│   │   ├── agent_0_ocr.py       # AWS Textract
│   │   ├── agent_1_pii.py       # GDPR PII masking
│   │   ├── agent_2_decimal.py   # Amount validation
│   │   ├── agent_3_ai_analyst.py# Bedrock Claude risk scoring
│   │   └── agents_4_to_7.py     # Audit, Notifier, Dashboard, Integrator
│   ├── tier2_intelligence/      # Agents 8-10 (ML, Learning, Currency)
│   ├── tier3_merchant/          # Agents 11-13 (Merchant, Quality, Trend)
│   ├── tier4_security/          # Agents 14-16 (Security, FraudRing, Behavioral)
│   └── agents_9_to_16.py        # Agents 9-16 implementation
│
├── api/
│   ├── routes.py                # 11 endpoints
│   ├── middleware.py            # JWT + X-Ray + RateLimit + SecurityHeaders
│   ├── rate_limiter.py          # Token bucket per user
│   └── models.py                # API models (re-exports shared/models.py)
│
├── services/
│   ├── database.py              # PostgreSQL SSL CERT_REQUIRED
│   ├── xray_tracer.py           # AWS X-Ray tracing
│   ├── secrets_manager.py       # AWS Secrets Manager
│   ├── cloudwatch_logger.py     # Structured CloudWatch logs
│   └── aws_service.py           # Textract + Bedrock wrappers
│
└── utils/
    └── security.py              # Validators + injection detection
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health | Public | Health check |
| POST | /api/analyze | JWT | Run 17-agent pipeline |
| GET | /api/invoices | JWT | List invoices |
| GET | /api/invoices/{id} | JWT | Get invoice |
| GET | /api/metrics | JWT | Dashboard KPIs |
| GET | /api/agents/status | JWT | Agent health |
| GET | /api/fraud-scenarios | JWT | Fraud patterns |
| GET | /api/audit-logs | JWT | Audit trail |
| POST | /api/feedback | JWT | Analyst feedback |
| GET | /api/xray/trace/{id} | JWT | X-Ray trace |
| GET | /api/rate-limit/stats | Admin | Rate limiter stats |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `COGNITO_USER_POOL_ID` | Prod | Cognito User Pool ID |
| `COGNITO_CLIENT_ID` | Prod | Cognito App Client ID |
| `AWS_REGION` | Prod | us-east-1 |
| `DB_SECRET_NAME` | Prod | Secrets Manager secret name |
| `DB_HOST` | Dev | PostgreSQL host |
| `DB_PASSWORD` | Dev | PostgreSQL password |
| `SNS_ALERT_TOPIC_ARN` | Optional | Fraud alert notifications |
| `ALLOWED_ORIGINS` | Prod | CORS origins (comma-separated) |

## Test

```bash
# Unit tests
pytest tests/backend/ -v

# Security tests
pytest tests/backend/test_security.py -v

# E2E
pytest tests/integration/ -v
```

## Deploy

Tự động qua GitHub Actions khi push to main.
Xem `.github/workflows/backend.yml`.
