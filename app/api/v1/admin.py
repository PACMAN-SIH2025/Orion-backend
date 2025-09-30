"""
Admin API Endpoints
Handles admin authentication, data ingestion, and system logs.
"""

import asyncio
import concurrent.futures
import subprocess
import sys
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from core.security import get_current_admin, get_current_regular_user, UserRequired
from models.admin_models import (
    AdminLoginRequest,
    AdminLoginResponse,
    IngestionRequest,
    IngestionResponse,
    LogsResponse,
    Crawl4AIScrapeRequest,
    Crawl4AIScrapeResponse,
    Crawl4AIStatusResponse
)
from models.user_models import Admin, User, UserKnowledgeSource
from services.ingestion_service import IngestionService
from workers.tasks import process_ingestion_task
from core.config import get_settings

router = APIRouter()
security = HTTPBearer()

# In-memory storage for tracking Crawl4AI tasks (in production, use Redis or database)
crawl_tasks = {}

# Get settings for ChromaDB configuration
settings = get_settings()


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(login_data: AdminLoginRequest):
    """
    Admin authentication endpoint.
    Returns JWT token for authenticated admin users.
    """
    # TODO: Implement admin authentication logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Admin login not implemented yet"
    )


@router.post("/ingestion", response_model=IngestionResponse)
async def trigger_ingestion(
    ingestion_data: IngestionRequest,
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Trigger data ingestion process.
    Accepts URLs or file uploads for processing.
    """
    # TODO: Implement ingestion trigger logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Data ingestion not implemented yet"
    )


@router.get("/logs", response_model=LogsResponse)
async def get_system_logs(
    limit: int = 100,
    offset: int = 0,
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Retrieve system logs for monitoring and debugging.
    """
    # TODO: Implement log retrieval logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Log retrieval not implemented yet"
    )


@router.get("/status")
async def get_ingestion_status(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get status of ongoing ingestion processes.
    """
    # TODO: Implement status check logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Status check not implemented yet"
    )


@router.post("/crawl4ai-scrape", response_model=Crawl4AIScrapeResponse)
async def crawl4ai_scrape(
    scrape_request: Crawl4AIScrapeRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger Crawl4AI web scraping for a given URL.
    Executes insert_docs.py as a subprocess and returns task tracking info.
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Convert URL to string for processing
        url_str = str(scrape_request.url)
        
        # Initialize task tracking
        crawl_tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0.0,
            "url": url_str,
            "collection_name": scrape_request.collection_name,
            "chunks_processed": 0,
            "total_chunks": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": None,
            "result": None,
            "error_message": None
        }
        
        # Add background task with optimized defaults for better performance
        background_tasks.add_task(
            run_crawl4ai_scraping,
            task_id,
            url_str,
            scrape_request.collection_name or "docs",
            scrape_request.max_depth or 2,  # Reduced default depth for better performance
            scrape_request.chunk_size or 1000,
            scrape_request.max_concurrent or 5  # Add concurrent limit
        )
        
        return Crawl4AIScrapeResponse(
            task_id=task_id,
            status="started",
            message=f"Crawl4AI scraping started for {url_str}",
            url=url_str,
            collection_name=scrape_request.collection_name or "docs",
            estimated_completion=datetime.utcnow() + timedelta(minutes=10)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scraping: {str(e)}"
        )


@router.get("/crawl4ai-status/{task_id}", response_model=Crawl4AIStatusResponse)
async def get_crawl4ai_status(task_id: str):
    """
    Get the status of a Crawl4AI scraping task.
    """
    if task_id not in crawl_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task_data = crawl_tasks[task_id]
    return Crawl4AIStatusResponse(**task_data)


@router.get("/crawl4ai-tasks")
async def list_crawl4ai_tasks():
    """
    List all Crawl4AI scraping tasks.
    """
    return {"tasks": list(crawl_tasks.values())}


@router.get("/chromadb-status")
async def get_chromadb_status():
    """
    Get ChromaDB status and collection information.
    """
    try:
        # Get ChromaDB configuration
        chroma_db_dir = os.getenv('CHROMA_DB_DIR', './chroma_db')
        collection_name = os.getenv('CHROMA_COLLECTION_NAME', 'docs')
        
        # Check if ChromaDB directory exists
        chroma_path = Path(chroma_db_dir)
        exists = chroma_path.exists()
        
        return {
            "status": "configured",
            "chroma_db_dir": chroma_db_dir,
            "collection_name": collection_name,
            "directory_exists": exists,
            "absolute_path": str(chroma_path.absolute()),
            "message": f"ChromaDB configured to use directory: {chroma_db_dir}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "ChromaDB configuration error"
        }


@router.get("/test-crawl4ai")
async def test_crawl4ai():
    """
    Test Crawl4AI script execution directly.
    """
    try:
        # Get the path to insert_docs.py
        backend_root = Path(__file__).parent.parent.parent.parent
        insert_docs_path = backend_root / "workers" / "crawl4AI-agent-v2" / "insert_docs.py"
        
        if not insert_docs_path.exists():
            return {"error": f"insert_docs.py not found at {insert_docs_path}"}
        
        # Test command
        cmd = ["python", str(insert_docs_path), "--help"]
        
        # Execute the subprocess using threading for Windows compatibility
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(backend_root),
                timeout=30
            )
            
            return {
                "backend_root": str(backend_root),
                "insert_docs_path": str(insert_docs_path),
                "path_exists": insert_docs_path.exists(),
                "return_code": result.returncode,
                "stdout": result.stdout[:500],  # Limit output
                "stderr": result.stderr[:500]
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out", "type": "TimeoutError"}
        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}
            
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


async def run_crawl4ai_scraping(
    task_id: str, 
    url: str, 
    collection_name: str, 
    max_depth: int, 
    chunk_size: int,
    max_concurrent: int = 5
):
    """
    Background task to run Crawl4AI scraping via subprocess.
    Uses ThreadPoolExecutor to run synchronous subprocess in async context.
    """
    try:
        # Update task status to processing
        crawl_tasks[task_id].update({
            "status": "processing",
            "progress": 10.0,
            "updated_at": datetime.utcnow()
        })
        
        # Get the path to insert_docs.py
        backend_root = Path(__file__).parent.parent.parent.parent
        insert_docs_path = backend_root / "workers" / "crawl4AI-agent-v2" / "insert_docs.py"
        
        print(f"Backend root: {backend_root}")
        print(f"Insert docs path: {insert_docs_path}")
        print(f"Path exists: {insert_docs_path.exists()}")
        
        if not insert_docs_path.exists():
            raise FileNotFoundError(f"insert_docs.py not found at {insert_docs_path}")
        
        # Get ChromaDB configuration from environment or use defaults
        chroma_db_dir = os.getenv('CHROMA_DB_DIR', './chroma_db')
        embedding_model = os.getenv('CHROMA_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        
        # Prepare command arguments with ChromaDB configuration
        cmd = [
            "python",
            str(insert_docs_path),
            url,
            "--collection", collection_name,
            "--db-dir", chroma_db_dir,
            "--embedding-model", embedding_model,
            "--max-depth", str(max_depth),
            "--chunk-size", str(chunk_size),
            "--max-concurrent", str(max_concurrent)  # Add concurrent limit
        ]
        
        print(f"Executing command: {' '.join(cmd)}")
        print(f"Working directory: {backend_root}")
        
        # Update progress
        crawl_tasks[task_id].update({
            "progress": 25.0,
            "updated_at": datetime.utcnow()
        })
        
        # Execute the subprocess using asyncio's thread pool for Windows compatibility
        def run_subprocess():
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(backend_root),
                    timeout=300,  # 5 minute timeout
                    encoding='utf-8',
                    errors='ignore'
                )
                return result
            except subprocess.TimeoutExpired as e:
                print(f"Subprocess timed out: {e}")
                return None
            except Exception as e:
                print(f"Subprocess execution error: {e}")
                print(f"Exception type: {type(e).__name__}")
                return None
        
        # Update progress
        crawl_tasks[task_id].update({
            "progress": 50.0,
            "updated_at": datetime.utcnow()
        })
        
        # Run in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, run_subprocess)
        
        if result is None:
            raise Exception("Subprocess execution failed or timed out")
        
        if result.returncode == 0:
            # Success
            output_text = result.stdout
            
            # Parse output to extract chunk count if available
            chunks_processed = 0
            for line in output_text.split('\n'):
                if "chunks into ChromaDB" in line:
                    try:
                        chunks_processed = int(line.split()[1])
                    except (IndexError, ValueError):
                        pass
            
            crawl_tasks[task_id].update({
                "status": "completed",
                "progress": 100.0,
                "chunks_processed": chunks_processed,
                "completed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "result": {
                    "output": output_text,
                    "chunks_processed": chunks_processed,
                    "collection_name": collection_name
                }
            })
        else:
            # Error
            error_text = result.stderr
            print(f"Subprocess failed with return code: {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {error_text}")
            crawl_tasks[task_id].update({
                "status": "failed",
                "progress": 0.0,
                "updated_at": datetime.utcnow(),
                "error_message": error_text or f"Process failed with return code {result.returncode}"
            })
            
    except Exception as e:
        # Handle any unexpected errors
        error_msg = str(e)
        print(f"Exception in run_crawl4ai_scraping: {error_msg}")
        print(f"Exception type: {type(e).__name__}")
        crawl_tasks[task_id].update({
            "status": "failed",
            "progress": 0.0,
            "updated_at": datetime.utcnow(),
            "error_message": error_msg
        })


@router.post("/user-crawl4ai-scrape", response_model=Crawl4AIScrapeResponse)
async def user_crawl4ai_scrape(
    scrape_request: Crawl4AIScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(UserRequired())
):
    """
    Trigger Crawl4AI web scraping for a given URL for authenticated users.
    Creates user-specific knowledge sources and collections.
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Convert URL to string for processing
        url_str = str(scrape_request.url)
        
        # Create user-specific collection name
        user_collection = f"user_{current_user.username}_{scrape_request.collection_name or 'docs'}"
        
        # Initialize task tracking
        crawl_tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0.0,
            "url": url_str,
            "collection_name": user_collection,
            "user_id": current_user.username,
            "chunks_processed": 0,
            "total_chunks": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": None,
            "result": None,
            "error_message": None
        }
        
        # Add background task
        background_tasks.add_task(
            run_crawl4ai_scraping,
            task_id,
            url_str,
            user_collection,
            scrape_request.max_depth or 3,
            scrape_request.chunk_size or 1000,
            scrape_request.max_concurrent or 5
        )
        
        return Crawl4AIScrapeResponse(
            task_id=task_id,
            status="started",
            message=f"User Crawl4AI scraping started for {url_str}",
            url=url_str,
            collection_name=user_collection,
            estimated_completion=datetime.utcnow() + timedelta(minutes=10)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start user scraping: {str(e)}"
        )


@router.get("/user-tasks")
async def get_user_crawl4ai_tasks(current_user: User = Depends(UserRequired())):
    """
    List all Crawl4AI scraping tasks for the authenticated user.
    """
    user_tasks = []
    for task_id, task_data in crawl_tasks.items():
        if task_data.get("user_id") == current_user.username:
            user_tasks.append(task_data)
    
    return {"tasks": user_tasks}


@router.get("/user-status/{task_id}", response_model=Crawl4AIStatusResponse)
async def get_user_crawl4ai_status(task_id: str, current_user: User = Depends(UserRequired())):
    """
    Get the status of a user's Crawl4AI scraping task.
    """
    if task_id not in crawl_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task_data = crawl_tasks[task_id]
    
    # Check if user owns this task
    if task_data.get("user_id") != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this task"
        )
    
    return Crawl4AIStatusResponse(**task_data)
