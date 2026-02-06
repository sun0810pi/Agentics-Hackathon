"""
Job Data Models
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class JobCreate(BaseModel):
    file_name: str
    file_size: int

class JobResponse(BaseModel):
    job_id: str
    user_email: str
    file_name: str
    file_size: int
    status: str
    created_at: str
    updated_at: Optional[str] = None
    execution_arn: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int