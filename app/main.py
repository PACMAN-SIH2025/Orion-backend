"""
FastAPI Main Application
Entry point for the Orion backend API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import admin, chat, auth
from core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Orion Backend API",
    description="RAG-powered educational assistant backend",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts,
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Orion Backend API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "orion-backend",
        "version": "1.0.0"
    }