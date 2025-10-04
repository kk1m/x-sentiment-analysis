"""
Post Model
Represents a single X (Twitter) post collected for analysis
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.src.storage.database import Base


class Post(Base):
    __tablename__ = "posts"
    
    # Primary Key
    post_id = Column(String, primary_key=True, index=True)
    
    # Foreign Keys
    author_id = Column(String, ForeignKey("authors.user_id"), nullable=False, index=True)
    batch_job_id = Column(String, ForeignKey("batch_jobs.batch_job_id"), nullable=True, index=True)
    
    # Content
    text = Column(Text, nullable=False)
    language = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, index=True)
    has_media = Column(Boolean, nullable=False, default=False)
    
    # Data Lineage
    collected_at = Column(DateTime, nullable=False)
    
    # Relationships
    author = relationship("Author", back_populates="posts")
    batch_job = relationship("BatchJob", back_populates="posts")
    engagement = relationship("Engagement", back_populates="post", uselist=False)
    sentiment_scores = relationship("SentimentScore", back_populates="post")
    bot_signal = relationship("BotSignal", back_populates="post", uselist=False)
    
    def __repr__(self):
        return f"<Post(post_id={self.post_id}, author_id={self.author_id}, created_at={self.created_at})>"
