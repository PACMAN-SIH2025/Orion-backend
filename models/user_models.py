"""
User Models
Pydantic/Database models for users and authentication.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None


class User(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserInDB(User):
    """User model with hashed password for database storage."""
    hashed_password: str


class Admin(User):
    """Admin user model."""
    is_admin: bool = True
    permissions: Optional[List[str]] = Field(default_factory=list)
    department: Optional[str] = None


class AdminInDB(Admin):
    """Admin model with hashed password for database storage."""
    hashed_password: str


class UserCreate(BaseModel):
    """User creation model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class AdminCreate(UserCreate):
    """Admin creation model."""
    permissions: Optional[List[str]] = Field(default_factory=list)
    department: Optional[str] = None


class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class AdminUpdate(UserUpdate):
    """Admin update model."""
    permissions: Optional[List[str]] = None
    department: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change model."""
    current_password: str
    new_password: str = Field(..., min_length=6)


class PasswordReset(BaseModel):
    """Password reset model."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""
    reset_token: str
    new_password: str = Field(..., min_length=6)


class UserSession(BaseModel):
    """User session model."""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True


class LoginHistory(BaseModel):
    """Login history model."""
    user_id: str
    login_time: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    failure_reason: Optional[str] = None