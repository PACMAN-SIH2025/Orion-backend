"""
Celery Application Configuration
Celery app instance configuration for background task processing.
"""

from celery import Celery
from core.config import get_settings

settings = get_settings()

# Create Celery app instance
celery_app = Celery(
    "orion_backend",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["workers.tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "workers.tasks.process_ingestion_task": {"queue": "ingestion"},
        "workers.tasks.generate_embeddings_task": {"queue": "embeddings"},
        "workers.tasks.cleanup_task": {"queue": "maintenance"},
    },
    
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone configuration
    timezone="UTC",
    enable_utc=True,
    
    # Task result expiration
    result_expires=3600,  # 1 hour
    
    # Task routing key
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Task retry configuration
    task_annotations={
        "*": {
            "rate_limit": "100/m",  # 100 tasks per minute
            "time_limit": 300,      # 5 minutes max per task
            "soft_time_limit": 240, # 4 minutes soft limit
        },
        "workers.tasks.process_ingestion_task": {
            "rate_limit": "10/m",   # Slower rate for ingestion
            "time_limit": 600,      # 10 minutes for ingestion
            "soft_time_limit": 540, # 9 minutes soft limit
        }
    },
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        "cleanup-old-tasks": {
            "task": "workers.tasks.cleanup_task",
            "schedule": 3600.0,  # Run every hour
        },
        "health-check": {
            "task": "workers.tasks.health_check_task",
            "schedule": 300.0,   # Run every 5 minutes
        },
    },
)

# Optional: Configure logging
celery_app.log.setup_logging_subsystem()

if __name__ == "__main__":
    celery_app.start()