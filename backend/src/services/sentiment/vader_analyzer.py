"""
VADER Sentiment Analyzer
Simple rule-based sentiment analysis (fallback/baseline)
"""
from typing import Dict
from backend.src.services.sentiment.base import SentimentAnalyzer


class VADERAnalyzer(SentimentAnalyzer):
    """VADER sentiment analyzer (baseline)"""
    
    def __init__(self):
        self._algorithm_id = "vader"
        self._algorithm_version = "v1.0"
    
    async def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment using simple keyword matching
        """
        text_lower = text.lower()
        
        bullish_keywords = ["moon", "bullish", "buy", "pump", "rocket", "🚀", "up", "gain"]
        bearish_keywords = ["dump", "bearish", "sell", "crash", "down", "loss"]
        
        bullish_count = sum(1 for kw in bullish_keywords if kw in text_lower)
        bearish_count = sum(1 for kw in bearish_keywords if kw in text_lower)
        
        if bullish_count > bearish_count:
            return {
                "classification": "Bullish",
                "confidence": 0.6,
                "algorithm_id": self.algorithm_id,
                "algorithm_version": self.algorithm_version
            }
        elif bearish_count > bullish_count:
            return {
                "classification": "Bearish",
                "confidence": 0.6,
                "algorithm_id": self.algorithm_id,
                "algorithm_version": self.algorithm_version
            }
        else:
            return {
                "classification": "Neutral",
                "confidence": 0.5,
                "algorithm_id": self.algorithm_id,
                "algorithm_version": self.algorithm_version
            }
    
    @property
    def algorithm_id(self) -> str:
        return self._algorithm_id
    
    @property
    def algorithm_version(self) -> str:
        return self._algorithm_version
