"""
Configuration Management
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # AWS
    AWS_REGION: str = "ap-southeast-1"
    AWS_ACCOUNT_ID: Optional[str] = None
    
    # Project
    PROJECT_NAME: str = "apiflow-fintech"
    ENVIRONMENT: str = "dev"
    
    # DynamoDB
    DYNAMODB_USERS_TABLE: str = f"apiflow-fintech-users-dev"
    DYNAMODB_JOBS_TABLE: str = f"apiflow-fintech-jobs-dev"
    
    # S3
    S3_BUCKET_UPLOADS: str = f"apiflow-fintech-uploaded-files-dev"
    
    # Step Functions
    STATE_MACHINE_ARN: Optional[str] = None
    
    # JWT
    JWT_SECRET_KEY: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list = [".xlsx", ".xls", ".csv"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()