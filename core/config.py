"""
Configuration Management
Pydantic settings for environment variable management.
"""

from functools import lru_cache
from typing import List
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # App Configuration
    debug: bool = Field(default=False, env="DEBUG")
    app_name: str = Field(default="Orion Backend", env="APP_NAME")
    version: str = Field(default="1.0.0", env="VERSION")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS and Security
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
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
    
    # AI/LLM Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    huggingface_api_key: str = Field(default="", env="HUGGINGFACE_API_KEY")
    
    # RAG Configuration
    embedding_model: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    llm_model: str = Field(default="gpt-3.5-turbo", env="LLM_MODEL")
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