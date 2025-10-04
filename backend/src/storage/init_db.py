"""
Database Initialization
Creates all tables based on SQLAlchemy models
"""
from backend.src.storage.database import engine, Base
from backend.src.models.author import Author
from backend.src.models.post import Post
from backend.src.models.engagement import Engagement
from backend.src.models.sentiment_score import SentimentScore
from backend.src.models.bot_signal import BotSignal
from backend.src.models.weighting_config import WeightingConfig
from backend.src.models.daily_aggregate import DailyAggregate
from backend.src.models.batch_job import BatchJob


def init_database():
    """
    Initialize database by creating all tables
    """
    print("Creating database tables...")
    
    # Import all models to ensure they're registered with Base
    # (already imported above)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✓ Database tables created successfully")
    print(f"  - authors")
    print(f"  - posts")
    print(f"  - engagements")
    print(f"  - sentiment_scores")
    print(f"  - bot_signals")
    print(f"  - weighting_configs")
    print(f"  - daily_aggregates")
    print(f"  - batch_jobs")


def drop_database():
    """
    Drop all tables (use with caution!)
    """
    print("WARNING: Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped")


def reset_database():
    """
    Drop and recreate all tables (use with caution!)
    """
    drop_database()
    init_database()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "init":
            init_database()
        elif command == "drop":
            drop_database()
        elif command == "reset":
            reset_database()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python init_db.py [init|drop|reset]")
    else:
        init_database()
