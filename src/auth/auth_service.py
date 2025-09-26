from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
from typing import Optional
import hashlib

class AuthService:
    """Enterprise authentication service"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.security = HTTPBearer()
    
    def create_workspace_token(self, workspace_id: str, user_email: str) -> str:
        """Create JWT token for workspace access"""
        payload = {
            "workspace_id": workspace_id,
            "user_email": user_email,
            "exp": datetime.utcnow() + timedelta(days=30)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_workspace_token(self, token: str) -> dict:
        """Verify and decode workspace token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
