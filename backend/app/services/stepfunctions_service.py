"""
Step Functions Service
"""

import boto3
from typing import Optional
from app.core.config import settings

class StepFunctionsService:
    def __init__(self):
        self.client = boto3.client('stepfunctions')
    
    async def get_execution_status(self, execution_arn: str) -> Optional[dict]:
        """Get execution status"""
        try:
            response = self.client.describe_execution(executionArn=execution_arn)
            return {
                "status": response["status"],
                "start_date": response["startDate"].isoformat(),
                "stop_date": response.get("stopDate", "").isoformat() if response.get("stopDate") else None,
                "output": response.get("output")
            }
        except Exception as e:
            return None