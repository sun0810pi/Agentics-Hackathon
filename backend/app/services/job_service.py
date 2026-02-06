"""
Job Service - File Upload & Step Functions Integration
"""

import boto3
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile
from app.core.config import settings

class JobService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.s3_client = boto3.client('s3')
        self.sf_client = boto3.client('stepfunctions')
        self.jobs_table = self.dynamodb.Table(settings.DYNAMODB_JOBS_TABLE)
    
    async def create_job_and_upload(self, file: UploadFile, user_email: str) -> dict:
        """Create job and upload file to S3"""
        job_id = str(uuid.uuid4())
        
        # Read file
        file_content = await file.read()
        file_size = len(file_content)
        
        # Upload to S3
        s3_key = f"uploads/{user_email}/{job_id}/{file.filename}"
        self.s3_client.put_object(
            Bucket=settings.S3_BUCKET_UPLOADS,
            Key=s3_key,
            Body=file_content,
            ContentType=file.content_type
        )
        
        # Create job record
        job_item = {
            "job_id": job_id,
            "user_email": user_email,
            "file_name": file.filename,
            "file_size": file_size,
            "s3_key": s3_key,
            "status": "UPLOADED",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.jobs_table.put_item(Item=job_item)
        
        # Start Step Functions execution
        if settings.STATE_MACHINE_ARN:
            execution_arn = await self._start_workflow(job_id, user_email, s3_key)
            job_item["execution_arn"] = execution_arn
            
            # Update job with execution ARN
            self.jobs_table.update_item(
                Key={"job_id": job_id, "user_email": user_email},
                UpdateExpression="SET execution_arn = :arn, #status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":arn": execution_arn,
                    ":status": "PROCESSING"
                }
            )
        
        return job_item
    
    async def _start_workflow(self, job_id: str, user_email: str, s3_key: str) -> str:
        """Start Step Functions workflow"""
        response = self.sf_client.start_execution(
            stateMachineArn=settings.STATE_MACHINE_ARN,
            input=f'{{"job_id": "{job_id}", "user_email": "{user_email}", "s3_key": "{s3_key}"}}'
        )
        return response["executionArn"]
    
    async def get_job(self, job_id: str, user_email: str) -> Optional[dict]:
        """Get job by ID"""
        try:
            response = self.jobs_table.get_item(
                Key={"job_id": job_id, "user_email": user_email}
            )
            return response.get("Item")
        except Exception:
            return None
    
    async def get_user_jobs(self, user_email: str, limit: int = 50) -> List[dict]:
        """Get user's jobs"""
        try:
            response = self.jobs_table.query(
                IndexName="UserEmailIndex",
                KeyConditionExpression="user_email = :email",
                ExpressionAttributeValues={":email": user_email},
                Limit=limit,
                ScanIndexForward=False  # Descending order
            )
            return response.get("Items", [])
        except Exception:
            return []