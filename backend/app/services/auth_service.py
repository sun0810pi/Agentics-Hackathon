"""
Authentication Service
"""

import boto3
import uuid
from datetime import datetime
from typing import Optional
from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.models.user import UserCreate

class AuthService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(settings.DYNAMODB_USERS_TABLE)
    
    async def create_user(self, user: UserCreate) -> dict:
        """Create new user"""
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user.password)
        
        user_item = {
            "email": user.email,
            "user_id": user_id,
            "hashed_password": hashed_password,
            "full_name": user.full_name or "",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.table.put_item(Item=user_item)
        
        # Remove password from response
        user_item.pop("hashed_password")
        return user_item
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        try:
            response = self.table.get_item(Key={"email": email})
            return response.get("Item")
        except Exception:
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate user"""
        user = await self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        return user