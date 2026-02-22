"""backend/lambda_handler.py — AWS Lambda entry point"""
from mangum import Mangum
from main import app
handler = Mangum(app, lifespan="on")
