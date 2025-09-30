"""
Database Configuration and Models
SQLite database setup with SQLAlchemy for persistent storage.
"""

import os
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Float, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any

from core.config import get_settings

settings = get_settings()

# Create database directory if it doesn't exist
db_dir = os.path.dirname(settings.database_url.replace("sqlite:///", ""))
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Database setup
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User database model."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)


class Website(Base):
    """Website database model."""
    __tablename__ = "websites"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    base_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    source_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_accessed = Column(DateTime, nullable=True)


class KnowledgeSource(Base):
    """Knowledge source database model."""
    __tablename__ = "knowledge_sources"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    website_name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # url, pdf, document
    source_url = Column(String, nullable=True)
    source_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    collection_name = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    chunks_processed = Column(Integer, default=0)
    total_chunks = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    tags = Column(JSON, default=list)  # Store as JSON
    source_metadata = Column(JSON, default=dict)  # Store as JSON (renamed from metadata)
    error_message = Column(Text, nullable=True)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database and create tables."""
    create_tables()
    print("Database initialized successfully")


# Database service functions
class DatabaseService:
    """Database service for user and knowledge source operations."""
    
    @staticmethod
    def create_user(db, user_data: dict) -> User:
        """Create a new user."""
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_username(db, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user_last_login(db, username: str):
        """Update user's last login time."""
        db.query(User).filter(User.username == username).update(
            {"last_login": datetime.utcnow()}
        )
        db.commit()
    
    @staticmethod
    def create_knowledge_source(db, source_data: dict) -> KnowledgeSource:
        """Create a new knowledge source."""
        db_source = KnowledgeSource(**source_data)
        db.add(db_source)
        db.commit()
        db.refresh(db_source)
        return db_source
    
    @staticmethod
    def get_knowledge_sources_by_user(db, user_id: str, website_name: Optional[str] = None) -> List[KnowledgeSource]:
        """Get knowledge sources for a user, optionally filtered by website."""
        query = db.query(KnowledgeSource).filter(KnowledgeSource.user_id == user_id)
        if website_name:
            query = query.filter(KnowledgeSource.website_name == website_name)
        return query.order_by(KnowledgeSource.created_at.desc()).all()
    
    @staticmethod
    def get_knowledge_source_by_id(db, source_id: str) -> Optional[KnowledgeSource]:
        """Get knowledge source by ID."""
        return db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    
    @staticmethod
    def update_knowledge_source(db, source_id: str, update_data: dict):
        """Update knowledge source."""
        db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).update(update_data)
        db.commit()
    
    @staticmethod
    def delete_knowledge_source(db, source_id: str):
        """Delete knowledge source."""
        db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).delete()
        db.commit()
    
    @staticmethod
    def create_or_update_website(db, website_data: dict) -> Website:
        """Create or update website."""
        existing = db.query(Website).filter(
            Website.name == website_data["name"],
            Website.user_id == website_data["user_id"]
        ).first()
        
        if existing:
            # Update existing website
            for key, value in website_data.items():
                if key != "id":  # Don't update ID
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new website
            db_website = Website(**website_data)
            db.add(db_website)
            db.commit()
            db.refresh(db_website)
            return db_website
    
    @staticmethod
    def get_websites_by_user(db, user_id: str) -> List[Website]:
        """Get websites for a user."""
        return db.query(Website).filter(Website.user_id == user_id).order_by(Website.name).all()
    
    @staticmethod
    def update_website_source_count(db, user_id: str, website_name: str):
        """Update website source count."""
        count = db.query(KnowledgeSource).filter(
            KnowledgeSource.user_id == user_id,
            KnowledgeSource.website_name == website_name
        ).count()
        
        db.query(Website).filter(
            Website.user_id == user_id,
            Website.name == website_name
        ).update({"source_count": count, "updated_at": datetime.utcnow()})
        db.commit()