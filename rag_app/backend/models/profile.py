"""
Profile model - maps to public.profiles table.

Extends Supabase auth.users with additional user information.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import Base


class Profile(Base):
    """User profile model."""
    
    __tablename__ = "profiles"
    
    id: Column[UUID] = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="User ID (references auth.users)"
    )
    email: Column[Optional[str]] = Column(
        String(255),
        nullable=True,
        comment="User email"
    )
    full_name: Column[Optional[str]] = Column(
        String(255),
        nullable=True,
        comment="User's full name"
    )
    avatar_url: Column[Optional[str]] = Column(
        String(500),
        nullable=True,
        comment="URL to user's avatar image"
    )
    created_at: Column[datetime] = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Creation timestamp"
    )
    updated_at: Column[datetime] = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )
    
    # Relationships
    sessions: relationship = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    documents: relationship = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
