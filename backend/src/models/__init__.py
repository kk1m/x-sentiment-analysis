"""
Models package
Import all models here to ensure they're registered with SQLAlchemy
"""
from backend.src.models.author import Author
from backend.src.models.batch_job import BatchJob
from backend.src.models.post import Post
from backend.src.models.engagement import Engagement
from backend.src.models.sentiment_score import SentimentScore
from backend.src.models.bot_signal import BotSignal
from backend.src.models.weighting_config import WeightingConfig
from backend.src.models.daily_aggregate import DailyAggregate

__all__ = [
    "Author",
    "BatchJob",
    "Post",
    "Engagement",
    "SentimentScore",
    "BotSignal",
    "WeightingConfig",
    "DailyAggregate"
]
