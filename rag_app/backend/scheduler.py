"""Simple scheduler for background tasks.

This module provides a lightweight scheduler that can run tasks periodically
without requiring Redis or RabbitMQ. Uses Python's built-in threading.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)


class SimpleScheduler:
    """Simple task scheduler using threading."""
    
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._threads: Dict[str, threading.Thread] = {}
        self._running = False
    
    def add_task(
        self,
        task_id: str,
        func: Callable,
        interval_seconds: int,
        *args,
        **kwargs
    ) -> None:
        """Add a task to the scheduler.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            interval_seconds: Interval between executions in seconds
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        self._tasks[task_id] = {
            'func': func,
            'interval': interval_seconds,
            'args': args,
            'kwargs': kwargs,
            'last_run': None,
            'next_run': datetime.utcnow() + timedelta(seconds=interval_seconds)
        }
        logger.info(f"Added task '{task_id}' with interval {interval_seconds}s")
    
    def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            logger.warning("Scheduler is already running")
            return
        
        self._running = True
        logger.info("Starting scheduler")
        
        for task_id in self._tasks:
            thread = threading.Thread(
                target=self._run_task_loop,
                args=(task_id,),
                daemon=True
            )
            self._threads[task_id] = thread
            thread.start()
        
        logger.info(f"Scheduler started with {len(self._tasks)} tasks")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        logger.info("Stopping scheduler")
        
        for task_id, thread in self._threads.items():
            logger.info(f"Waiting for task '{task_id}' to finish...")
        
        # Give threads time to finish
        time.sleep(2)
        
        logger.info("Scheduler stopped")
    
    def _run_task_loop(self, task_id: str) -> None:
        """Run a task in a loop."""
        task = self._tasks[task_id]
        
        while self._running:
            try:
                now = datetime.utcnow()
                
                if now >= task['next_run']:
                    logger.info(f"Executing task '{task_id}'")
                    task['func'](*task['args'], **task['kwargs'])
                    task['last_run'] = now
                    task['next_run'] = now + timedelta(seconds=task['interval'])
                
                # Sleep for a short interval to check if we should run
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in task '{task_id}': {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        status = {
            'running': self._running,
            'tasks': {}
        }
        
        for task_id, task in self._tasks.items():
            status['tasks'][task_id] = {
                'interval': task['interval'],
                'last_run': task['last_run'].isoformat() if task['last_run'] else None,
                'next_run': task['next_run'].isoformat() if task['next_run'] else None
            }
        
        return status


# Global scheduler instance
_scheduler = SimpleScheduler()


def _init_default_tasks() -> None:
    """Initialize default tasks including session cleanup."""
    from tasks.session_cleanup import cleanup_expired_sessions
    
    # Add session cleanup task (runs every hour, cleans sessions older than 30 days)
    _scheduler.add_task(
        task_id="session_cleanup",
        func=cleanup_expired_sessions,
        interval_seconds=3600,  # 1 hour
        days_threshold=30
    )
    logger.info("Default tasks initialized: session_cleanup")


def get_scheduler() -> SimpleScheduler:
    """Get the global scheduler instance."""
    return _scheduler


def start_scheduler() -> None:
    """Start the global scheduler."""
    _init_default_tasks()
    _scheduler.start()


def stop_scheduler() -> None:
    """Stop the global scheduler."""
    _scheduler.stop()
