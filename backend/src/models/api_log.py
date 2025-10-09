"""
APILog Model
Tracks all external API calls for observability and debugging
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
from backend.src.storage.database import Base
from datetime import datetime


class APILog(Base):
    __tablename__ = "api_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Service Info
    service = Column(String, nullable=False, index=True)  # 'openrouter', 'x_api', etc.
    endpoint = Column(String, nullable=False)  # Full URL
    model = Column(String, nullable=True)  # Model name (for LLM calls)
    
    # Request Details
    system_prompt = Column(Text, nullable=True)  # For LLM calls
    user_message = Column(Text, nullable=True)  # For LLM calls
    request_params = Column(JSON, nullable=True)  # All other params as JSON
    
    # Response Details
    response_raw = Column(Text, nullable=True)  # Raw response body
    response_parsed = Column(JSON, nullable=True)  # Parsed/structured response
    response_time_ms = Column(Integer, nullable=True)  # Latency in milliseconds
    
    # Cost Tracking
    tokens_used = Column(Integer, nullable=True)  # Total tokens (prompt + completion)
    cost_usd = Column(Float, nullable=True)  # Estimated cost in USD
    
    # Context
    post_id = Column(String, nullable=True, index=True)  # Related post ID
    algorithm_id = Column(String, nullable=True)  # Related algorithm
    
    # Status
    status = Column(String, nullable=False, index=True)  # 'success', 'error', 'timeout'
    error_message = Column(Text, nullable=True)  # Error details if failed
    
    def __repr__(self):
        return f"<APILog(service={self.service}, status={self.status}, time={self.response_time_ms}ms)>"
    
    @property
    def is_success(self):
        """Check if API call was successful"""
        return self.status == 'success'
    
    @property
    def is_expensive(self):
        """Check if call was expensive (>$0.01)"""
        return self.cost_usd and self.cost_usd > 0.01
