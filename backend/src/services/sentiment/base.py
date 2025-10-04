"""
Base Sentiment Analyzer
Abstract interface for sentiment analysis algorithms
"""
from abc import ABC, abstractmethod
from typing import Dict


class SentimentAnalyzer(ABC):
    """Abstract base class for sentiment analyzers"""
    
    @abstractmethod
    async def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
        
        Returns:
            Dict with:
                - classification: "Bullish", "Bearish", or "Neutral"
                - confidence: float 0.0-1.0
                - algorithm_id: str
                - algorithm_version: str
        """
        pass
    
    @property
    @abstractmethod
    def algorithm_id(self) -> str:
        """Return algorithm identifier"""
        pass
    
    @property
    @abstractmethod
    def algorithm_version(self) -> str:
        """Return algorithm version"""
        pass
