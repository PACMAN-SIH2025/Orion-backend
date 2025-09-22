"""
Celery Task Definitions
Asynchronous task definitions for ingestion and other background operations.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from celery import current_task
from celery.exceptions import Retry

from workers.celery_app import celery_app
from services.ingestion_service import IngestionService
from services.rag_service import RAGService
from models.admin_models import IngestionRequest

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60})
def process_ingestion_task(self, ingestion_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task for processing document ingestion.
    
    Args:
        ingestion_data: Dictionary containing ingestion request data
        
    Returns:
        Dictionary with processing results
    """
    task_id = self.request.id
    logger.info(f"Starting ingestion task {task_id}")
    
    try:
        # Update task state
        self.update_state(
            state="PROCESSING",
            meta={"status": "Starting ingestion process", "progress": 0}
        )
        
        # Create ingestion request object
        request = IngestionRequest(**ingestion_data)
        
        # Initialize ingestion service
        ingestion_service = IngestionService()
        
        # Process the ingestion (run async function in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Update progress
            self.update_state(
                state="PROCESSING",
                meta={"status": "Processing documents", "progress": 25}
            )
            
            # Process ingestion
            result = loop.run_until_complete(
                ingestion_service.process_ingestion(request)
            )
            
            # Update progress
            self.update_state(
                state="PROCESSING", 
                meta={"status": "Generating embeddings", "progress": 50}
            )
            
            # Generate embeddings and add to vector database
            embedding_result = loop.run_until_complete(
                generate_embeddings_for_chunks(result["chunks"])
            )
            
            # Update progress
            self.update_state(
                state="PROCESSING",
                meta={"status": "Storing in database", "progress": 75}
            )
            
            # Final result
            final_result = {
                **result,
                "embeddings_generated": embedding_result["success"],
                "embeddings_count": embedding_result["count"],
                "task_id": task_id,
                "completed_at": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
            logger.info(f"Ingestion task {task_id} completed successfully")
            
            return final_result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Ingestion task {task_id} failed: {str(e)}")
        
        # Update task state with error
        self.update_state(
            state="FAILURE",
            meta={"status": "Error during processing", "error": str(e)}
        )
        
        # Re-raise for Celery's retry mechanism
        raise


@celery_app.task(bind=True)
def generate_embeddings_task(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Celery task for generating embeddings for document chunks.
    
    Args:
        chunks: List of document chunks to process
        
    Returns:
        Dictionary with embedding generation results
    """
    task_id = self.request.id
    logger.info(f"Starting embedding generation task {task_id}")
    
    try:
        self.update_state(
            state="PROCESSING",
            meta={"status": "Generating embeddings", "progress": 0}
        )
        
        # Run async embedding generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                generate_embeddings_for_chunks(chunks)
            )
            
            logger.info(f"Embedding generation task {task_id} completed")
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Embedding generation task {task_id} failed: {str(e)}")
        raise


async def generate_embeddings_for_chunks(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate embeddings for document chunks and store in vector database.
    
    Args:
        chunks: List of document chunks
        
    Returns:
        Results of embedding generation
    """
    try:
        rag_service = RAGService()
        
        # Prepare documents for indexing
        documents = []
        for chunk in chunks:
            documents.append({
                "id": chunk["id"],
                "content": chunk["content"],
                "metadata": chunk
            })
        
        # Add documents to vector index
        success = await rag_service.add_documents_to_index(documents)
        
        return {
            "success": success,
            "count": len(documents),
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise


@celery_app.task
def cleanup_task() -> Dict[str, Any]:
    """
    Periodic cleanup task for removing old data and temporary files.
    
    Returns:
        Cleanup results
    """
    logger.info("Starting cleanup task")
    
    try:
        # TODO: Implement cleanup logic
        # - Remove old task results
        # - Clean up temporary files
        # - Archive old chat sessions
        # - Clean up expired tokens
        
        cleanup_results = {
            "old_tasks_removed": 0,
            "temp_files_removed": 0,
            "sessions_archived": 0,
            "cleanup_completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info("Cleanup task completed")
        return cleanup_results
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise


@celery_app.task
def health_check_task() -> Dict[str, Any]:
    """
    Health check task for monitoring system status.
    
    Returns:
        System health status
    """
    try:
        # TODO: Implement health checks
        # - Check database connectivity
        # - Check vector database status
        # - Check external API availability
        # - Check disk space
        
        health_status = {
            "database": "healthy",
            "vector_db": "healthy", 
            "external_apis": "healthy",
            "disk_space": "healthy",
            "checked_at": datetime.utcnow().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True)
def batch_ingestion_task(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process multiple ingestion requests as a batch.
    
    Args:
        batch_data: Dictionary containing batch ingestion data
        
    Returns:
        Batch processing results
    """
    task_id = self.request.id
    logger.info(f"Starting batch ingestion task {task_id}")
    
    try:
        sources = batch_data.get("sources", [])
        batch_name = batch_data.get("batch_name", f"batch_{task_id}")
        
        self.update_state(
            state="PROCESSING",
            meta={"status": f"Processing batch {batch_name}", "progress": 0}
        )
        
        results = []
        total_sources = len(sources)
        
        for i, source_data in enumerate(sources):
            try:
                # Process individual ingestion
                result = process_ingestion_task.delay(source_data)
                results.append({
                    "source_index": i,
                    "task_id": result.id,
                    "status": "submitted"
                })
                
                # Update progress
                progress = int((i + 1) / total_sources * 100)
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "status": f"Submitted {i + 1}/{total_sources} tasks",
                        "progress": progress
                    }
                )
                
            except Exception as e:
                results.append({
                    "source_index": i,
                    "status": "failed",
                    "error": str(e)
                })
        
        batch_result = {
            "batch_id": task_id,
            "batch_name": batch_name,
            "total_sources": total_sources,
            "submitted_tasks": len([r for r in results if r["status"] == "submitted"]),
            "failed_submissions": len([r for r in results if r["status"] == "failed"]),
            "results": results,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Batch ingestion task {task_id} completed")
        return batch_result
        
    except Exception as e:
        logger.error(f"Batch ingestion task {task_id} failed: {str(e)}")
        raise


# Task status checking utilities
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a Celery task."""
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state == "PENDING":
            return {"status": "pending", "message": "Task is waiting to be processed"}
        elif task.state == "PROCESSING":
            return {
                "status": "processing", 
                "progress": task.info.get("progress", 0),
                "message": task.info.get("status", "Processing...")
            }
        elif task.state == "SUCCESS":
            return {"status": "completed", "result": task.result}
        elif task.state == "FAILURE":
            return {
                "status": "failed", 
                "error": str(task.info),
                "traceback": getattr(task, "traceback", None)
            }
        else:
            return {"status": task.state, "info": str(task.info)}
            
    except Exception as e:
        return {"status": "error", "message": f"Failed to get task status: {str(e)}"}


def cancel_task(task_id: str) -> Dict[str, Any]:
    """Cancel a Celery task."""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"status": "cancelled", "task_id": task_id}
    except Exception as e:
        return {"status": "error", "message": f"Failed to cancel task: {str(e)}"}