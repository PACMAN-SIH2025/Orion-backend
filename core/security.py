"""
Security and Authentication
JWT authentication logic and dependency functions.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import get_settings
from models.user_models import Admin, TokenData

settings = get_settings()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        raise credentials_exception


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Get current authenticated user from token."""
    return verify_token(credentials.credentials)


async def get_current_admin(current_user: TokenData = Depends(get_current_user)) -> Admin:
    """Get current admin user."""
    # TODO: Implement admin user lookup from database
    # This is a placeholder - you'll need to implement actual user lookup
    admin = Admin(
        username=current_user.username,
        email=f"{current_user.username}@admin.com",
        is_active=True,
        is_admin=True
    )
    
    if not admin.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return admin


def authenticate_admin(username: str, password: str) -> Optional[Admin]:
    """Authenticate admin user."""
    # TODO: Implement actual admin authentication against database
    # This is a placeholder implementation
    return None


class AdminRequired:
    """Dependency class for admin-only endpoints."""
    
    def __call__(self, current_admin: Admin = Depends(get_current_admin)) -> Admin:
        return current_admin