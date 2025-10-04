"""
Engagement Model
Represents engagement metrics for a post (likes, retweets, etc.)
"""
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from backend.src.storage.database import Base


class Engagement(Base):
    __tablename__ = "engagements"
    
    # Primary Key (same as post_id - one-to-one relationship)
    post_id = Column(String, ForeignKey("posts.post_id"), primary_key=True, index=True)
    
    # Engagement Metrics
    like_count = Column(Integer, nullable=False, default=0)
    retweet_count = Column(Integer, nullable=False, default=0)
    reply_count = Column(Integer, nullable=False, default=0)
    quote_count = Column(Integer, nullable=False, default=0)
    
    # Optional Metrics (may require paid X API tier)
    bookmark_count = Column(Integer, nullable=True)
    impression_count = Column(Integer, nullable=True)
    view_count = Column(Integer, nullable=True)
    
    # Relationships
    post = relationship("Post", back_populates="engagement")
    
    def __repr__(self):
        return f"<Engagement(post_id={self.post_id}, likes={self.like_count}, retweets={self.retweet_count})>"
    
    @property
    def total_engagement(self):
        """Calculate total engagement score"""
        return (
            self.like_count + 
            (self.retweet_count * 2) +  # Retweets weighted higher
            self.reply_count + 
            self.quote_count
        )
