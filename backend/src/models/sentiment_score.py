"""
SentimentScore Model
Represents sentiment analysis result for a post
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from backend.src.storage.database import Base


class SentimentClassification(enum.Enum):
    """Sentiment classification enum"""
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"


class SentimentScore(Base):
    __tablename__ = "sentiment_scores"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    post_id = Column(String, ForeignKey("posts.post_id"), nullable=False, index=True)
    
    # Algorithm Information
    algorithm_id = Column(String, nullable=False, index=True)  # e.g., "openai-gpt4", "finbert", "vader"
    algorithm_version = Column(String, nullable=False)  # e.g., "gpt-4-0613", "v1.0"
    
    # Sentiment Result
    classification = Column(Enum(SentimentClassification), nullable=False, index=True)
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Metadata
    created_at = Column(DateTime, nullable=False, index=True)
    processing_time_ms = Column(Integer, nullable=True)  # Optional performance tracking
    
    # Relationships
    post = relationship("Post", back_populates="sentiment_scores")
    
    def __repr__(self):
        return f"<SentimentScore(post_id={self.post_id}, algorithm={self.algorithm_id}, classification={self.classification.value}, confidence={self.confidence})>"
    
    @property
    def is_high_confidence(self):
        """Check if confidence is above threshold"""
        return self.confidence >= 0.7
