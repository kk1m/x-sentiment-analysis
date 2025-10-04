"""
Database Configuration
SQLAlchemy engine and session factory
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentiment_analysis.db")

# Create engine
# SQLite-specific: check_same_thread=False allows multiple threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_session():
    """
    Get database session
    Usage:
        session = get_session()
        try:
            # Use session
            session.add(obj)
            session.commit()
        finally:
            session.close()
    """
    return SessionLocal()


def get_db():
    """
    Dependency for FastAPI endpoints
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
