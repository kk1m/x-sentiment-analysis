"""
WeightingConfig Model
Represents configuration for weighted sentiment scoring
"""
from sqlalchemy import Column, String, Text, Float, Date
from backend.src.storage.database import Base


class WeightingConfig(Base):
    __tablename__ = "weighting_configs"
    
    # Primary Key
    version = Column(String, primary_key=True)  # e.g., "v1.0", "v2.0"
    
    # Formulas (stored as text, evaluated at runtime)
    visibility_formula = Column(Text, nullable=False)  # e.g., "log(likes + retweets * 2)"
    influence_formula = Column(Text, nullable=False)  # e.g., "sqrt(followers)"
    bot_penalty_formula = Column(Text, nullable=False)  # e.g., "1 - bot_score"
    
    # Multipliers
    verification_multiplier = Column(Float, nullable=False, default=1.5)
    
    # Metadata
    effective_date = Column(Date, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<WeightingConfig(version={self.version}, effective_date={self.effective_date})>"
    
    @classmethod
    def get_default(cls):
        """Return default weighting configuration"""
        return cls(
            version="v1.0",
            visibility_formula="log(1 + likes + retweets * 2 + replies + quotes)",
            influence_formula="log(1 + followers)",
            bot_penalty_formula="max(0, 1 - bot_score * 2)",
            verification_multiplier=1.5,
            description="Default weighting configuration"
        )
