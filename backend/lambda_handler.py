"""
backend/lambda_handler.py
==========================
AWS Lambda entry point using Mangum (FastAPI → Lambda adapter).
This wraps the FastAPI app for deployment as a containerized Lambda.
"""

from mangum import Mangum
from main import app

# Mangum adapts ASGI (FastAPI) to AWS Lambda's event format
handler = Mangum(app, lifespan="on")
