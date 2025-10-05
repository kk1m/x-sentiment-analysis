"""
OpenAI Sentiment Analyzer
Uses OpenAI/OpenRouter API for sentiment analysis
"""
import os
import json
import asyncio
import httpx
from typing import Dict
from backend.src.services.sentiment.base import SentimentAnalyzer
from backend.src.config import config


class OpenAIAnalyzer(SentimentAnalyzer):
    """Sentiment analyzer using OpenAI/OpenRouter API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.openai_config = config.sentiment_openai_config
        self.system_prompt = config.sentiment_system_prompt
        
        self._algorithm_id = "openai"
        self._algorithm_version = self.openai_config.get('model', 'unknown')
    
    async def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment using OpenRouter API
        
        Args:
            text: Tweet text to analyze
            
        Returns:
            Dict with classification, confidence, algorithm info
        """
        if not self.api_key:
            # Fallback to keyword matching if no API key
            return await self._fallback_keyword_analysis(text)
        
        try:
            # Call OpenRouter API with retries
            result = await self._call_openrouter_with_retry(text)
            return result
            
        except Exception as e:
            print(f"   ⚠️ OpenRouter API failed: {e}")
            # Fallback to keyword matching
            return await self._fallback_keyword_analysis(text)
    
    async def _call_openrouter_with_retry(self, text: str) -> Dict:
        """Call OpenRouter API with retry logic"""
        max_retries = self.openai_config.get('max_retries', 3)
        timeout = self.openai_config.get('timeout_seconds', 30)
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        self.openai_config.get('api_base_url') + "/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.openai_config.get('model'),
                            "messages": [
                                {"role": "system", "content": self.system_prompt},
                                {"role": "user", "content": f"Analyze this tweet: {text}"}
                            ],
                            "temperature": self.openai_config.get('temperature', 0.3),
                            "max_tokens": self.openai_config.get('max_tokens', 200)
                        }
                    )
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    # Parse response
                    return self._parse_openrouter_response(result)
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                # Wait before retry (exponential backoff)
                await asyncio.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
    
    def _parse_openrouter_response(self, response: Dict) -> Dict:
        """Parse OpenRouter API response"""
        try:
            content = response["choices"][0]["message"]["content"]
            
            # Try to parse as JSON
            parsed = json.loads(content)
            
            return {
                "classification": parsed.get("sentiment", "Neutral"),
                "confidence": float(parsed.get("confidence", 0.5)),
                "algorithm_id": self.algorithm_id,
                "algorithm_version": self.algorithm_version
            }
        except:
            # If parsing fails, return neutral
            return {
                "classification": "Neutral",
                "confidence": 0.5,
                "algorithm_id": self.algorithm_id,
                "algorithm_version": self.algorithm_version
            }
    
    async def _fallback_keyword_analysis(self, text: str) -> Dict:
        """Fallback keyword-based analysis"""
        text_lower = text.lower()
        
        bullish_keywords = ["moon", "bullish", "buy", "pump", "rocket", "🚀", "up", "gain", "accumulate"]
        bearish_keywords = ["dump", "bearish", "sell", "crash", "down", "loss", "exit"]
        
        bullish_score = sum(1 for kw in bullish_keywords if kw in text_lower)
        bearish_score = sum(1 for kw in bearish_keywords if kw in text_lower)
        
        if bullish_score > bearish_score:
            classification = "Bullish"
            confidence = min(0.6 + (bullish_score * 0.1), 0.95)
        elif bearish_score > bullish_score:
            classification = "Bearish"
            confidence = min(0.6 + (bearish_score * 0.1), 0.95)
        else:
            classification = "Neutral"
            confidence = 0.5
        
        return {
            "classification": classification,
            "confidence": confidence,
            "algorithm_id": "keyword-fallback",
            "algorithm_version": "v1.0"
        }
    
    @property
    def algorithm_id(self) -> str:
        return self._algorithm_id
    
    @property
    def algorithm_version(self) -> str:
        return self._algorithm_version
