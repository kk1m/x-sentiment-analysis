"""
BatchJob Model
Represents a single execution of the daily data collection process
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum
from sqlalchemy.orm import relationship
import enum
from backend.src.storage.database import Base


class JobStatus(enum.Enum):
    """Batch job status enum"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BatchJob(Base):
    __tablename__ = "batch_jobs"
    
    # Primary Key
    batch_job_id = Column(String, primary_key=True)  # UUID
    
    # Execution Metadata
    started_at = Column(DateTime, nullable=False, index=True)
    finished_at = Column(DateTime, nullable=True)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.RUNNING, index=True)
    
    # Results
    posts_collected = Column(Integer, nullable=False, default=0)
    posts_stored = Column(Integer, nullable=False, default=0)
    errors_count = Column(Integer, nullable=False, default=0)
    
    # Error Details
    errors = Column(Text, nullable=True)  # JSON or text log of errors
    
    # Configuration
    search_queries = Column(Text, nullable=True)  # JSON array of hashtags searched
    
    # Relationships
    posts = relationship("Post", back_populates="batch_job")
    
    def __repr__(self):
        return f"<BatchJob(batch_job_id={self.batch_job_id}, status={self.status.value}, posts_collected={self.posts_collected})>"
    
    @property
    def duration_seconds(self):
        """Calculate job duration in seconds"""
        if self.finished_at and self.started_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None
    
    @property
    def success_rate(self):
        """Calculate success rate (posts stored / posts collected)"""
        if self.posts_collected == 0:
            return 0.0
        return (self.posts_stored / self.posts_collected) * 100
