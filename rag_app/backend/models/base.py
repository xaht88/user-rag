"""
Base class for all SQLAlchemy models.

Provides common functionality and configuration.
"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    
    # Custom types
    JSONB = JSON

