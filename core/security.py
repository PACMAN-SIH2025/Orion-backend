"""
Security utilities for Supabase authentication and authorization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from core.supabase_client import supabase_service
from models.user_models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Keep existing password utilities for backwards compatibility
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


async def get_current_user_from_supabase(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from Supabase token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Validate token with Supabase
        response = await supabase_service.get_user_from_token(credentials.credentials)
        
        if not response or not hasattr(response, 'user') or not response.user:
            raise credentials_exception
        
        user_data = response.user
        email = getattr(user_data, 'email', None)
        user_metadata = getattr(user_data, 'user_metadata', {}) or {}
        
        # Create User model from Supabase user data
        user = User(
            username=user_metadata.get("username", email.split("@")[0] if email else "unknown"),
            email=email or "unknown@example.com",
            full_name=user_metadata.get("full_name", ""),
            is_active=True,
            created_at=getattr(user_data, 'created_at', None),
            last_login=getattr(user_data, 'last_sign_in_at', None)
        )
        
        return user
        
    except Exception as e:
        raise credentials_exception

# Dependency classes for different user types
class UserRequired:
    """Dependency to require authenticated user."""
    
    def __call__(self, current_user: User = Depends(get_current_user_from_supabase)) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        return current_user

class AdminRequired:
    """Dependency to require admin user."""
    
    def __call__(self, current_user: User = Depends(get_current_user_from_supabase)) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # Check if user has admin role in metadata
        # You can customize this logic based on your admin identification method
        is_admin = (
            current_user.email in ["admin@orion.com"] or  # Hardcoded admin emails
            "admin" in (current_user.full_name or "").lower()  # Or check metadata
        )
        
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return current_user

# Legacy functions (kept for backwards compatibility)
def authenticate_user(username: str, password: str):
    """Legacy function - use Supabase auth instead."""
    raise NotImplementedError("Use Supabase authentication")

def authenticate_admin(username: str, password: str):
    """Legacy function - use Supabase auth instead."""
    raise NotImplementedError("Use Supabase authentication")

def get_current_regular_user():
    """Legacy function - use UserRequired() instead."""
    return UserRequired()

def get_current_admin():
    """Legacy function - use AdminRequired() instead."""
    return AdminRequired()