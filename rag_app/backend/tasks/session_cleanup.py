"""Session cleanup task for removing expired sessions.

This module provides functionality to clean up expired sessions from the database.
Can be run as a standalone script or scheduled via cron/Celery.
"""

import logging
import sys
import os
from datetime import datetime, timedelta  # noqa: F401

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Session as SessionModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cleanup_expired_sessions(days_threshold: int = 30) -> int:
    """Clean up expired sessions older than specified days.
    
    Args:
        days_threshold: Number of days after which sessions are considered expired.
                       Default is 30 days.
    
    Returns:
        Number of sessions deleted
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
    
    logger.info(f"Starting session cleanup. Cutoff date: {cutoff_date}")
    
    db = SessionLocal()
    try:
        # Delete sessions older than threshold
        result = db.query(SessionModel).filter(
            SessionModel.expires_at < cutoff_date
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Cleaned up {result} sessions older than {days_threshold} days")
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during session cleanup: {e}")
        raise
    finally:
        db.close()


def cleanup_all_expired_sessions() -> int:
    """Clean up ALL expired sessions (regardless of age).
    
    This is useful for immediate cleanup of sessions that have already expired.
    
    Returns:
        Number of sessions deleted
    """
    logger.info("Starting cleanup of all expired sessions")
    
    db = SessionLocal()
    try:
        # Delete all sessions that are already expired
        result = db.query(SessionModel).filter(
            SessionModel.expires_at < datetime.utcnow()
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Cleaned up {result} expired sessions")
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during expired session cleanup: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    """Run cleanup task from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up expired sessions")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days after which sessions are considered expired (default: 30)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Clean up ALL expired sessions regardless of age"
    )
    
    args = parser.parse_args()
    
    try:
        if args.all:
            deleted = cleanup_all_expired_sessions()
        else:
            deleted = cleanup_expired_sessions(days_threshold=args.days)
        
        print(f"Cleanup completed. {deleted} sessions deleted.")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        sys.exit(1)
