"""
Author Model
Represents an X (Twitter) user who created a post
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.src.storage.database import Base


class Author(Base):
    __tablename__ = "authors"
    
    # Primary Key
    user_id = Column(String, primary_key=True, index=True)
    
    # Profile Information
    username = Column(String, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    profile_description = Column(String, nullable=True)
    
    # Metrics
    followers_count = Column(Integer, nullable=False, default=0)
    following_count = Column(Integer, nullable=False, default=0)
    
    # Status
    verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)
    
    # Timestamps
    first_seen = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    
    # Relationships
    posts = relationship("Post", back_populates="author")
    
    def __repr__(self):
        return f"<Author(user_id={self.user_id}, username={self.username}, verified={self.verified})>"
