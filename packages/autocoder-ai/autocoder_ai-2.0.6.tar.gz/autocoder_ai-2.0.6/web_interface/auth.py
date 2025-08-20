"""
Authentication module for WebSocket and API endpoints
"""

import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Bearer token security
security = HTTPBearer(auto_error=False)


class AuthManager:
    """Manages authentication tokens and session validation"""
    
    def __init__(self):
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
        self.secret_key = SECRET_KEY
        
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=ALGORITHM)
        
        # Store token for validation
        token_id = secrets.token_urlsafe(16)
        self.active_tokens[token_id] = {
            "token": encoded_jwt,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expire.isoformat(),
            "data": data
        }
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def create_session_token(self, session_id: str, project_id: str = None) -> str:
        """Create a token for a specific session"""
        token_data = {
            "session_id": session_id,
            "project_id": project_id,
            "type": "session",
            "created_at": datetime.utcnow().isoformat()
        }
        return self.create_access_token(token_data)
    
    def create_api_token(self, client_id: str = None) -> str:
        """Create an API token for CLI or external clients"""
        token_data = {
            "client_id": client_id or secrets.token_urlsafe(16),
            "type": "api",
            "created_at": datetime.utcnow().isoformat()
        }
        return self.create_access_token(token_data)
    
    def validate_websocket_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a token for WebSocket connection"""
        payload = self.verify_token(token)
        if payload and payload.get("type") in ["session", "api"]:
            return payload
        return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke an active token"""
        # Find and remove token from active tokens
        for token_id, token_data in list(self.active_tokens.items()):
            if token_data["token"] == token:
                del self.active_tokens[token_id]
                return True
        return False
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from memory"""
        now = datetime.utcnow()
        expired = []
        
        for token_id, token_data in self.active_tokens.items():
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if expires_at < now:
                expired.append(token_id)
        
        for token_id in expired:
            del self.active_tokens[token_id]
        
        return len(expired)


# Global auth manager instance
auth_manager = AuthManager()


async def get_current_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Optional[str]:
    """Dependency to get the current bearer token"""
    if credentials:
        return credentials.credentials
    return None


async def verify_token(token: str = Depends(get_current_token)) -> Dict[str, Any]:
    """Dependency to verify the current token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = auth_manager.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def optional_verify_token(token: str = Depends(get_current_token)) -> Optional[Dict[str, Any]]:
    """Optional token verification - doesn't raise exception if missing"""
    if token:
        return auth_manager.verify_token(token)
    return None
