"""
User Models
Pydantic/Database models for users and authentication.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, HttpUrl


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


class UserKnowledgeSource(BaseModel):
    """User-specific knowledge source model."""
    id: str
    user_id: str
    website_name: str = Field(..., description="Website name for organization")
    source_type: str = Field(..., pattern=r"^(url|pdf|document)$")
    source_url: Optional[HttpUrl] = None
    source_name: str = Field(..., description="Display name for the source")
    description: Optional[str] = None
    collection_name: str = Field(..., description="ChromaDB collection name")
    status: str = Field(default="pending", pattern=r"^(pending|processing|completed|failed)$")
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    chunks_processed: int = Field(default=0)
    total_chunks: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = Field(default=0)
    tags: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    error_message: Optional[str] = None


class UserKnowledgeSourceCreate(BaseModel):
    """Create user knowledge source model."""
    website_name: str = Field(..., description="Website name for organization")
    source_type: str = Field(..., pattern=r"^(url|pdf|document)$")
    source_url: Optional[HttpUrl] = None
    source_name: str = Field(..., description="Display name for the source")
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    max_depth: Optional[int] = Field(default=3, ge=1, le=5)
    chunk_size: Optional[int] = Field(default=1000, ge=100, le=5000)


class UserKnowledgeSourceUpdate(BaseModel):
    """Update user knowledge source model."""
    source_name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class Website(BaseModel):
    """Website organization model."""
    name: str = Field(..., description="Website name")
    user_id: str
    base_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    source_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime
    last_accessed: Optional[datetime] = None


class UserLoginRequest(BaseModel):
    """User login request model."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLoginResponse(BaseModel):
    """User login response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict