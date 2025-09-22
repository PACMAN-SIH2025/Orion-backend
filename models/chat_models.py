"""
Chat API Models
Pydantic models for the chat API requests and responses.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    include_sources: bool = Field(default=True, description="Whether to include source documents")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4000)


class SourceDocument(BaseModel):
    """Source document model."""
    title: str
    content_snippet: str = Field(..., max_length=500)
    url: Optional[str] = None
    document_type: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str
    message_id: str
    timestamp: datetime
    sources: Optional[List[SourceDocument]] = None
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    processing_time_ms: Optional[int] = None
    token_usage: Optional[Dict[str, int]] = None


class ChatHistory(BaseModel):
    """Chat history entry model."""
    message_id: str
    session_id: str
    user_message: str
    ai_response: str
    timestamp: datetime
    sources_used: Optional[List[str]] = None
    feedback_rating: Optional[int] = Field(default=None, ge=1, le=5)


class ConversationSummary(BaseModel):
    """Conversation summary model."""
    session_id: str
    first_message_time: datetime
    last_message_time: datetime
    message_count: int
    topics: List[str]
    summary: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation response model for admin monitoring."""
    conversation: ConversationSummary
    recent_messages: List[ChatHistory]


class FeedbackRequest(BaseModel):
    """User feedback request model."""
    message_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = Field(default=None, max_length=1000)
    category: Optional[str] = Field(default=None, description="Feedback category")


class ChatMetrics(BaseModel):
    """Chat metrics model for analytics."""
    total_conversations: int
    total_messages: int
    average_response_time_ms: float
    average_rating: Optional[float] = None
    common_topics: List[str]
    daily_message_count: Dict[str, int]


class QuickReply(BaseModel):
    """Quick reply suggestion model."""
    text: str
    category: str
    confidence: float = Field(ge=0.0, le=1.0)


class ChatSuggestion(BaseModel):
    """Chat suggestion model."""
    suggestions: List[QuickReply]
    context_based: bool = False