"""
Sentiment Service
Coordinates sentiment analysis across multiple algorithms
"""
from datetime import datetime
from typing import Dict, Optional
from backend.src.services.sentiment.openai_analyzer import OpenAIAnalyzer
from backend.src.services.sentiment.vader_analyzer import VADERAnalyzer
from backend.src.storage.database import get_session
from backend.src.models.sentiment_score import SentimentScore, SentimentClassification


class SentimentService:
    """Coordinates sentiment analysis"""
    
    def __init__(self):
        self.analyzers = {
            "openai": OpenAIAnalyzer(),
            "openai-gpt4": OpenAIAnalyzer(),  # Backward compatibility
            "vader": VADERAnalyzer()
        }
    
    async def classify_sentiment(
        self,
        text: str,
        algorithm: str = "openai-gpt4",
        post_id: str = None
    ) -> Dict:
        """
        Classify sentiment of text using specified algorithm
        
        Args:
            text: Text to analyze
            algorithm: Algorithm to use
            post_id: Optional post ID for logging
        
        Returns:
            Dict with classification, confidence, algorithm info
        """
        analyzer = self.analyzers.get(algorithm)
        if not analyzer:
            # Fallback to VADER
            analyzer = self.analyzers["vader"]
        
        try:
            result = await analyzer.analyze(text, post_id=post_id)
            return result
        except Exception as e:
            # Fallback to VADER on error
            if algorithm != "vader":
                return await self.analyzers["vader"].analyze(text, post_id=post_id)
            raise
    
    async def classify_and_store(
        self,
        post_id: str,
        text: str,
        algorithm: str = "openai-gpt4"
    ) -> SentimentScore:
        """
        Classify sentiment and store in database
        
        Args:
            post_id: Post ID
            text: Post text
            algorithm: Algorithm to use
        
        Returns:
            SentimentScore object
        """
        result = await self.classify_sentiment(text, algorithm, post_id=post_id)
        
        # Map string to enum
        classification_map = {
            "Bullish": SentimentClassification.BULLISH,
            "Bearish": SentimentClassification.BEARISH,
            "Neutral": SentimentClassification.NEUTRAL
        }
        
        session = get_session()
        try:
            score = SentimentScore(
                post_id=post_id,
                algorithm_id=result["algorithm_id"],
                algorithm_version=result["algorithm_version"],
                classification=classification_map[result["classification"]],
                confidence=result["confidence"],
                score=result.get("score"),  # New: 0-100 score
                reasoning=result.get("reasoning"),  # New: LLM reasoning
                created_at=datetime.utcnow()
            )
            session.add(score)
            session.commit()
            session.refresh(score)
            return score
        finally:
            session.close()
