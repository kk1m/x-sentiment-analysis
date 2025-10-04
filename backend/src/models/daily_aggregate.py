"""
DailyAggregate Model
Represents aggregated sentiment for a specific topic on a specific day
"""
from sqlalchemy import Column, String, Integer, Float, Date, Enum, ForeignKey
import enum
from backend.src.storage.database import Base


class Topic(enum.Enum):
    """Topic enum"""
    BITCOIN = "Bitcoin"
    MSTR = "MSTR"
    BITCOIN_TREASURIES = "BitcoinTreasuries"


class DominantSentiment(enum.Enum):
    """Dominant sentiment enum"""
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"


class DailyAggregate(Base):
    __tablename__ = "daily_aggregates"
    
    # Primary Key (composite)
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Dimensions
    date = Column(Date, nullable=False, index=True)
    topic = Column(Enum(Topic), nullable=False, index=True)
    algorithm_id = Column(String, nullable=False, index=True)
    
    # Volume Metrics
    total_posts = Column(Integer, nullable=False, default=0)
    total_posts_after_bot_filter = Column(Integer, nullable=False, default=0)
    unique_authors = Column(Integer, nullable=False, default=0)
    verified_authors = Column(Integer, nullable=False, default=0)
    
    # Sentiment Distribution
    bullish_count = Column(Integer, nullable=False, default=0)
    bearish_count = Column(Integer, nullable=False, default=0)
    neutral_count = Column(Integer, nullable=False, default=0)
    
    # Weighted Scores
    weighted_score = Column(Float, nullable=False)  # Aggregate weighted sentiment (-1 to 1, negative=bearish, positive=bullish)
    weighted_bullish_score = Column(Float, nullable=False, default=0.0)
    weighted_bearish_score = Column(Float, nullable=False, default=0.0)
    dominant_sentiment = Column(Enum(DominantSentiment), nullable=False)
    
    # Engagement Aggregates
    total_likes = Column(Integer, nullable=False, default=0)
    total_retweets = Column(Integer, nullable=False, default=0)
    avg_engagement_per_post = Column(Float, nullable=False, default=0.0)
    
    # Quality Metrics
    bot_detection_rate = Column(Float, nullable=False, default=0.0)  # % of posts flagged as bots
    high_confidence_sentiment_pct = Column(Float, nullable=False, default=0.0)  # % with confidence >0.8
    
    # Configuration
    weighting_config_version = Column(String, ForeignKey("weighting_configs.version"), nullable=True)
    
    def __repr__(self):
        return f"<DailyAggregate(date={self.date}, topic={self.topic.value}, algorithm={self.algorithm_id}, dominant={self.dominant_sentiment.value})>"
    
    @property
    def bullish_percentage(self):
        """Calculate bullish percentage"""
        if self.total_posts == 0:
            return 0.0
        return (self.bullish_count / self.total_posts) * 100
    
    @property
    def bearish_percentage(self):
        """Calculate bearish percentage"""
        if self.total_posts == 0:
            return 0.0
        return (self.bearish_count / self.total_posts) * 100
    
    @property
    def neutral_percentage(self):
        """Calculate neutral percentage"""
        if self.total_posts == 0:
            return 0.0
        return (self.neutral_count / self.total_posts) * 100
