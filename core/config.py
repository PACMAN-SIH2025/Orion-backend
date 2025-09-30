"""
Configuration Management
Pydantic settings for environment variable management.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # App Configuration
    debug: bool = Field(default=False, env="DEBUG")
    app_name: str = Field(default="Orion Backend", env="APP_NAME")
    version: str = Field(default="1.0.0", env="VERSION")
    
    # Security (only keep SECRET_KEY for general cryptographic operations)
    secret_key: str = Field(..., env="SECRET_KEY")
    
    # Supabase Configuration
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    
    # CORS and Security
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"],
        env="ALLOWED_ORIGINS"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Redis (for Celery and caching)
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Vector Database (e.g., Pinecone, Weaviate, or ChromaDB)
    vector_db_url: str = Field(..., env="VECTOR_DB_URL")
    vector_db_api_key: str = Field(default="", env="VECTOR_DB_API_KEY")
    
    # ChromaDB Configuration
    chroma_db_dir: str = Field(default="./chroma_db", env="CHROMA_DB_DIR")
    chroma_collection_name: str = Field(default="docs", env="CHROMA_COLLECTION_NAME")
    chroma_embedding_model: str = Field(default="all-MiniLM-L6-v2", env="CHROMA_EMBEDDING_MODEL")
    
    # AI/LLM Configuration
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    huggingface_api_key: str = Field(default="", env="HUGGINGFACE_API_KEY")
    
    # RAG Configuration
    embedding_model: str = Field(default="models/embedding-001", env="EMBEDDING_MODEL")
    llm_model: str = Field(default="gemini-1.5-flash", env="LLM_MODEL")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    max_tokens: int = Field(default=2000, env="MAX_TOKENS")
    
    # Ingestion Configuration
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    supported_file_types: List[str] = Field(
        default=[".pdf", ".txt", ".docx", ".md"],
        env="SUPPORTED_FILE_TYPES"
    )
    
    # Celery Configuration
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/orion.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()