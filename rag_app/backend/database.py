"""
Database connection and session management.

Uses Supabase PostgreSQL via SQLAlchemy.
"""

import os
import sys
import os as os_module
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Handle both relative and absolute imports
try:
    from .models import Base
except ImportError:
    sys.path.insert(0, os_module.path.dirname(os_module.path.abspath(__file__)))
    from models import Base

# Database URL from environment
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    os.getenv('SUPABASE_URL', '')
)

# Connection string for Supabase
# Format: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
if DATABASE_URL and 'supabase.co' in DATABASE_URL:
    # Use Supabase connection
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get Supabase credentials
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD', '')
    
    if SUPABASE_DB_PASSWORD:
        # Parse project ref from URL
        project_ref = SUPABASE_URL.split('.')[0].split('//')[1]
        DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@db.{project_ref}.supabase.co:5432/postgres"

# Create engine with connection pooling
# Use in-memory SQLite for testing if no DATABASE_URL is provided
if not DATABASE_URL or DATABASE_URL == '':
    DATABASE_URL = 'sqlite:///./test_rag_app.db'

engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv('DATABASE_POOL_SIZE', 10)),
    max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', 20)),
    pool_pre_ping=True,
    echo=os.getenv('DEBUG', 'false').lower() == 'true'
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Thread-local session factory
db_session = scoped_session(SessionLocal)


def get_db() -> Generator:
    """
    Dependency injector for database session.
    
    Yields a database session and ensures it's closed after use.
    
    Yields:
        Generator: Database session
    
    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = db_session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    
    Creates all tables defined in models.Base.
    Should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)


def cleanup_db():
    """
    Cleanup database connections.
    
    Should be called on application shutdown.
    """
    engine.dispose()
    db_session.remove()
