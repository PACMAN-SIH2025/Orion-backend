"""
Admin API Models
Pydantic models for admin API requests and responses.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class AdminLoginRequest(BaseModel):
    """Admin login request model."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class AdminLoginResponse(BaseModel):
    """Admin login response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin_info: Dict[str, Any]


class IngestionRequest(BaseModel):
    """Data ingestion request model (URL scraping removed - only file and text ingestion supported)."""
    source_type: str = Field(..., pattern=r"^(file|text)$")
    source_data: str = Field(..., description="File path or raw text")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=10)
    tags: Optional[List[str]] = Field(default_factory=list)


class IngestionResponse(BaseModel):
    """Data ingestion response model."""
    task_id: str
    status: str
    message: str
    estimated_completion: Optional[datetime] = None


class LogEntry(BaseModel):
    """Individual log entry model."""
    timestamp: datetime
    level: str
    message: str
    module: str
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LogsResponse(BaseModel):
    """Logs response model."""
    logs: List[LogEntry]
    total_count: int
    page: int
    per_page: int
    has_next: bool


class IngestionStatus(BaseModel):
    """Ingestion status model."""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: float = Field(ge=0.0, le=100.0)
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class SystemStats(BaseModel):
    """System statistics model."""
    total_documents: int
    total_chunks: int
    active_ingestion_tasks: int
    completed_ingestion_tasks: int
    failed_ingestion_tasks: int
    storage_used_mb: float
    last_ingestion: Optional[datetime] = None


class BulkIngestionRequest(BaseModel):
    """Bulk data ingestion request model."""
    sources: List[IngestionRequest]
    batch_name: Optional[str] = None
    notify_on_completion: bool = False
    notification_email: Optional[str] = None


class BulkIngestionResponse(BaseModel):
    """Bulk data ingestion response model."""
    batch_id: str
    task_ids: List[str]
    total_tasks: int
    message: str


class Crawl4AIScrapeRequest(BaseModel):
    """Crawl4AI web scraping request model."""
    url: HttpUrl = Field(..., description="URL to scrape")
    description: Optional[str] = Field(None, description="Optional description for the source")
    collection_name: Optional[str] = Field(default="docs", description="ChromaDB collection name")
    max_depth: Optional[int] = Field(default=3, ge=1, le=5, description="Maximum crawling depth")
    chunk_size: Optional[int] = Field(default=1000, ge=100, le=5000, description="Maximum chunk size in characters")
    max_concurrent: Optional[int] = Field(default=5, ge=1, le=10, description="Maximum concurrent connections")
    

class Crawl4AIScrapeResponse(BaseModel):
    """Crawl4AI web scraping response model."""
    task_id: str
    status: str = "started"
    message: str
    url: str
    collection_name: str
    estimated_completion: Optional[datetime] = None


class Crawl4AIStatusResponse(BaseModel):
    """Crawl4AI scraping status response model."""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: float = Field(ge=0.0, le=100.0)
    url: str
    collection_name: str
    chunks_processed: Optional[int] = None
    total_chunks: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None