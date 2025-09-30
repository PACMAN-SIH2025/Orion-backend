"""
Authentication API Endpoints
Handles user registration, login, and authentication with Supabase.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import HTTPBearer
import uuid
from datetime import datetime
import subprocess
import sys
import os

from core.supabase_client import supabase_service
from core.security import UserRequired, AdminRequired
from core.database import get_db, DatabaseService
from sqlalchemy.orm import Session
from models.user_models import (
    UserLoginRequest,
    UserLoginResponse,
    UserCreate,
    User,
    PasswordChange,
    UserKnowledgeSource,
    UserKnowledgeSourceCreate,
    UserKnowledgeSourceUpdate,
    Website
)

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate):
    """Register a new user with Supabase."""
    try:
        # Sign up with Supabase
        response = await supabase_service.sign_up_user(
            email=user_data.email,
            password=user_data.password,
            user_metadata={
                "username": user_data.username,
                "full_name": user_data.full_name
            }
        )
        
        if hasattr(response, 'user') and response.user:
            return {
                "message": "User registered successfully. Please check your email for verification.",
                "username": user_data.username,
                "email": user_data.email
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=UserLoginResponse)
async def login_user(login_data: UserLoginRequest, request: Request):
    """Authenticate user with Supabase and return access token."""
    try:
        # For backwards compatibility, support both email and username login
        email = login_data.username
        if "@" not in email:
            # If username provided, we'll need to handle this differently
            # For now, require email-based login
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please use your email address to login"
            )
        
        # Sign in with Supabase
        response = await supabase_service.sign_in_user(
            email=email,
            password=login_data.password
        )
        
        if not hasattr(response, 'user') or not response.user or not hasattr(response, 'session') or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_data = response.user
        session_data = response.session
        
        # Safely get user metadata
        user_metadata = getattr(user_data, 'user_metadata', {}) or {}
        email_addr = getattr(user_data, 'email', 'unknown@example.com')
        
        return UserLoginResponse(
            access_token=session_data.access_token,
            token_type="bearer",
            expires_in=getattr(session_data, 'expires_in', 3600),
            user_info={
                "id": getattr(user_data, 'id', str(uuid.uuid4())),
                "username": user_metadata.get("username", email_addr.split("@")[0] if email_addr else "unknown"),
                "email": email_addr,
                "full_name": user_metadata.get("full_name", "")
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(UserRequired())):
    """Get current user information."""
    return {
        "id": getattr(current_user, 'id', current_user.username),
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }

@router.post("/logout")
async def logout_user(current_user: User = Depends(UserRequired())):
    """Logout user."""
    try:
        # Note: Supabase handles logout on the client side
        # This endpoint exists for consistency but the actual logout
        # should be handled by the frontend calling supabase.auth.signOut()
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/reset-password")
async def reset_password(email: str):
    """Send password reset email."""
    try:
        response = await supabase_service.reset_password(email)
        return {"message": "Password reset email sent successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/websites", response_model=List[Website])
async def get_user_websites(
    current_user: User = Depends(UserRequired()),
    db: Session = Depends(get_db)
):
    """Get all websites for the current user."""
    try:
        user_id = getattr(current_user, 'id', current_user.username)
        websites = DatabaseService.get_websites_by_user(db, user_id)
        return [Website(
            name=website.name,
            user_id=website.user_id,
            base_url=website.base_url,
            description=website.description,
            source_count=website.source_count,
            created_at=website.created_at,
            updated_at=website.updated_at,
            last_accessed=website.last_accessed
        ) for website in websites]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/knowledge-sources", response_model=UserKnowledgeSource)
async def create_knowledge_source(
    source_data: UserKnowledgeSourceCreate,
    current_user: User = Depends(UserRequired()),
    db: Session = Depends(get_db)
):
    """Create a new knowledge source for the user."""
    try:
        user_id = getattr(current_user, 'id', current_user.username)
        source_id = str(uuid.uuid4())
        collection_name = f"user_{user_id}_{source_data.website_name.lower().replace(' ', '_')}"
        
        # Create or update website entry
        website_data = {
            "id": str(uuid.uuid4()),
            "name": source_data.website_name,
            "user_id": user_id,
            "base_url": str(source_data.source_url) if source_data.source_url else None,
            "description": source_data.description
        }
        DatabaseService.create_or_update_website(db, website_data)
        
        # Create knowledge source
        knowledge_source_data = {
            "id": source_id,
            "user_id": user_id,
            "website_name": source_data.website_name,
            "source_type": source_data.source_type,
            "source_url": str(source_data.source_url) if source_data.source_url else None,
            "source_name": source_data.source_name,
            "description": source_data.description,
            "collection_name": collection_name,
            "status": "pending",
            "progress": 0.0,
            "chunks_processed": 0,
            "total_chunks": None,
            "tags": source_data.tags,
            "source_metadata": {
                "max_depth": source_data.max_depth,
                "chunk_size": source_data.chunk_size
            },
            "error_message": None
        }
        
        db_source = DatabaseService.create_knowledge_source(db, knowledge_source_data)
        
        return UserKnowledgeSource(
            id=db_source.id,
            user_id=db_source.user_id,
            website_name=db_source.website_name,
            source_type=db_source.source_type,
            source_url=db_source.source_url,
            source_name=db_source.source_name,
            description=db_source.description,
            collection_name=db_source.collection_name,
            status=db_source.status,
            progress=db_source.progress,
            chunks_processed=db_source.chunks_processed,
            total_chunks=db_source.total_chunks,
            created_at=db_source.created_at,
            updated_at=db_source.updated_at,
            completed_at=db_source.completed_at,
            last_accessed=db_source.last_accessed,
            access_count=db_source.access_count,
            tags=db_source.tags,
            metadata=db_source.source_metadata,
            error_message=db_source.error_message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/knowledge-sources", response_model=List[UserKnowledgeSource])
async def get_user_knowledge_sources(
    website_name: Optional[str] = None,
    current_user: User = Depends(UserRequired()),
    db: Session = Depends(get_db)
):
    """Get all knowledge sources for the current user, optionally filtered by website."""
    try:
        user_id = getattr(current_user, 'id', current_user.username)
        sources = DatabaseService.get_knowledge_sources_by_user(db, user_id, website_name)
        return [UserKnowledgeSource(
            id=source.id,
            user_id=source.user_id,
            website_name=source.website_name,
            source_type=source.source_type,
            source_url=source.source_url,
            source_name=source.source_name,
            description=source.description,
            collection_name=source.collection_name,
            status=source.status,
            progress=source.progress,
            chunks_processed=source.chunks_processed,
            total_chunks=source.total_chunks,
            created_at=source.created_at,
            updated_at=source.updated_at,
            completed_at=source.completed_at,
            last_accessed=source.last_accessed,
            access_count=source.access_count,
            tags=source.tags,
            metadata=source.source_metadata,
            error_message=source.error_message
        ) for source in sources]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/knowledge-sources/{source_id}", response_model=UserKnowledgeSource)
async def get_knowledge_source(
    source_id: str,
    current_user: User = Depends(UserRequired()),
    db: Session = Depends(get_db)
):
    """Get a specific knowledge source."""
    try:
        user_id = getattr(current_user, 'id', current_user.username)
        source = DatabaseService.get_knowledge_source_by_id(db, source_id)
        
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge source not found"
            )
        
        # Check if user owns this source
        if source.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update access tracking
        DatabaseService.update_knowledge_source(db, source_id, {
            "last_accessed": datetime.utcnow(),
            "access_count": source.access_count + 1
        })
        
        return UserKnowledgeSource(
            id=source.id,
            user_id=source.user_id,
            website_name=source.website_name,
            source_type=source.source_type,
            source_url=source.source_url,
            source_name=source.source_name,
            description=source.description,
            collection_name=source.collection_name,
            status=source.status,
            progress=source.progress,
            chunks_processed=source.chunks_processed,
            total_chunks=source.total_chunks,
            created_at=source.created_at,
            updated_at=source.updated_at,
            completed_at=source.completed_at,
            last_accessed=source.last_accessed,
            access_count=source.access_count,
            tags=source.tags,
            metadata=source.source_metadata,
            error_message=source.error_message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/knowledge-sources/{source_id}")
async def delete_knowledge_source(
    source_id: str,
    current_user: User = Depends(UserRequired()),
    db: Session = Depends(get_db)
):
    """Delete a knowledge source."""
    try:
        user_id = getattr(current_user, 'id', current_user.username)
        source = DatabaseService.get_knowledge_source_by_id(db, source_id)
        
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge source not found"
            )
        
        # Check if user owns this source
        if source.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete source
        DatabaseService.delete_knowledge_source(db, source_id)
        
        # Update website source count
        DatabaseService.update_website_source_count(db, user_id, source.website_name)
        
        return {"message": "Knowledge source deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )