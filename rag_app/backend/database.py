"""Database connection and session management for Supabase PostgreSQL."""

import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase
from sqlalchemy.pool import StaticPool

# Supabase connection configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ibnzhdgjfihhjvbfimpu.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
DATABASE_URL = f"postgresql+psycopg2://postgres:{SUPABASE_KEY}@db.ibnzhdgjfihhjvbfimpu.supabase.co:5432/postgres"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=os.getenv("DEBUG", "false").lower() == "true",
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

# Dependency for FastAPI
def get_db() -> Generator:
    """
    Dependency for getting database session.
    
    Yields:
        Database session object
        
    Example:
        @app.get("/items/")
        async def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
