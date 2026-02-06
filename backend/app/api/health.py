"""
Health Check API
"""

from fastapi import APIRouter
import boto3
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with AWS services"""
    health_status = {
        "api": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    try:
        dynamodb = boto3.client('dynamodb')
        dynamodb.list_tables(Limit=1)
        health_status["services"]["dynamodb"] = "healthy"
    except Exception as e:
        health_status["services"]["dynamodb"] = f"unhealthy: {str(e)}"
    
    try:
        s3 = boto3.client('s3')
        s3.list_buckets()
        health_status["services"]["s3"] = "healthy"
    except Exception as e:
        health_status["services"]["s3"] = f"unhealthy: {str(e)}"
    
    try:
        sf = boto3.client('stepfunctions')
        sf.list_state_machines(maxResults=1)
        health_status["services"]["stepfunctions"] = "healthy"
    except Exception as e:
        health_status["services"]["stepfunctions"] = f"unhealthy: {str(e)}"
    
    return health_status