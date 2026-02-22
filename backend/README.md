# AgentFlow Backend

FastAPI + AWS Lambda backend for the 17-agent fraud detection pipeline.

## Quick Start (Local)

```bash
cd backend
pip install -r requirements.txt

# Run without AWS (demo mode)
DEMO_MODE=true uvicorn main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `COGNITO_USER_POOL_ID` | Yes | AWS Cognito User Pool ID |
| `COGNITO_CLIENT_ID` | Yes | AWS Cognito App Client ID |
| `AWS_REGION` | Yes | AWS region (e.g. us-east-1) |
| `DB_SECRET_NAME` | Yes (prod) | Secrets Manager name for DB creds |
| `DB_HOST` | Dev only | PostgreSQL host (if no Secrets Manager) |
| `DB_NAME` | Dev only | Database name |
| `DB_USER` | Dev only | Database user |
| `DB_PASSWORD` | Dev only | Database password |
| `SNS_ALERT_TOPIC_ARN` | Optional | SNS topic for fraud alerts |
| `ALLOWED_ORIGINS` | Yes | Comma-separated CORS origins |
| `DEBUG` | No | true/false |

## File Structure

```
backend/
├── main.py                    # FastAPI app factory
├── lambda_handler.py          # AWS Lambda entry point
├── config.py                  # Backend configuration
├── Dockerfile                 # Lambda container image
├── requirements.txt
│
├── agents/
│   ├── base.py                # BaseAgent + AgentContext classes
│   ├── orchestrator.py        # Runs all 17 agents, builds response
│   ├── tier1_core/agents.py   # Agents 0-7 (OCR, PII, Decimal, AI, etc.)
│   └── all_agents.py          # Agents 8-16 (ML, Merchant, Security)
│
├── api/
│   ├── routes.py              # All FastAPI endpoints
│   ├── middleware.py          # JWT + X-Ray + RateLimit + SecurityHeaders
│   └── rate_limiter.py        # Token bucket per-user rate limiter
│
├── services/
│   ├── database.py            # PostgreSQL (SSL CERT_REQUIRED)
│   ├── xray_tracer.py         # AWS X-Ray distributed tracing
│   ├── secrets_manager.py     # AWS Secrets Manager
│   └── cloudwatch_logger.py   # CloudWatch structured logging
│
└── utils/
    └── security.py            # Input validators + security helpers
```

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /health | Public | Health check |
| POST | /api/analyze | JWT | Run 17-agent pipeline |
| GET | /api/invoices | JWT | List processed invoices |
| GET | /api/invoices/{id} | JWT | Get single invoice |
| GET | /api/metrics | JWT | Dashboard KPIs |
| GET | /api/agents/status | JWT | Agent health status |
| GET | /api/fraud-scenarios | JWT | Known fraud patterns |
| GET | /api/audit-logs | JWT | Immutable audit trail |
| POST | /api/feedback | JWT | Submit analyst feedback |
| GET | /api/xray/trace/{id} | JWT | X-Ray trace for invoice |
| GET | /api/rate-limit/stats | Admin JWT | Rate limiter stats |

## Security Features

- JWT validation via AWS Cognito JWKS
- Per-user token bucket rate limiting (15 tokens, 10/min refill)
- SSL CERT_REQUIRED for all database connections
- Parameterized SQL queries (no string concatenation)
- Security headers on every response
- Input validation with whitelist approach
- Injection detection (SQL, XSS, path traversal, command injection)

## Deploy to Lambda

```bash
# Build and push Docker image
docker build -t agentflow-backend .
docker tag agentflow-backend:latest <AWS_ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/agentflow:latest
docker push <AWS_ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/agentflow:latest

# Update Lambda function
aws lambda update-function-code \
  --function-name agentflow-backend \
  --image-uri <AWS_ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/agentflow:latest
```

CI/CD does this automatically on push to main. See `.github/workflows/backend.yml`.
