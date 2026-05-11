"""Celery configuration for scheduled tasks.

This file configures Celery for background task scheduling.
For production, Redis or RabbitMQ is recommended as the message broker.
For development, we can use the built-in scheduler with file-based storage.
"""

from celery import Celery
from datetime import timedelta

# Create Celery app
app = Celery(
    'rag_backend',
    broker='redis://localhost:6379/0',  # Change to your Redis URL
    backend='redis://localhost:6379/0'
)

# Set configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    
    # Beat scheduler settings
    beat_schedule={
        'cleanup-expired-sessions': {
            'task': 'tasks.session_cleanup.cleanup_expired_sessions',
            'schedule': timedelta(hours=1),  # Run every hour
            'options': {'args': (30,)}  # Clean sessions older than 30 days
        },
    },
    
    # Task routing
    task_routes={
        'tasks.*': {'queue': 'default'},
    },
)

# Import tasks to register them
from . import tasks
