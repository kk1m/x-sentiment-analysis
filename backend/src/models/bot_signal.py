"""
BotSignal Model
Represents bot likelihood score for a post's author
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.src.storage.database import Base


class BotSignal(Base):
    __tablename__ = "bot_signals"
    
    # Primary Key
    id = Column(String, primary_key=True)  # UUID
    
    # Foreign Key
    post_id = Column(String, ForeignKey("posts.post_id"), nullable=False, index=True)
    
    # Bot Detection Result
    score = Column(Float, nullable=False)  # 0.0 (human) to 1.0 (bot)
    
    # Input Signals (for debugging and refinement)
    inputs = Column(JSON, nullable=True)  # Store indicators used: account_age, follower_ratio, etc.
    
    # Metadata
    created_at = Column(DateTime, nullable=False)
    detector_version = Column(String, nullable=False, default="v1.0")
    
    # Relationships
    post = relationship("Post", back_populates="bot_signal")
    
    def __repr__(self):
        return f"<BotSignal(post_id={self.post_id}, score={self.score:.2f})>"
    
    @property
    def is_likely_bot(self):
        """Check if score indicates likely bot (>0.7 threshold)"""
        return self.score > 0.7
    
    @property
    def is_likely_human(self):
        """Check if score indicates likely human (<0.3 threshold)"""
        return self.score < 0.3
