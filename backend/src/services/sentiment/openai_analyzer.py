"""
OpenAI Sentiment Analyzer
Uses OpenAI/OpenRouter API for sentiment analysis
"""
import os
import json
import asyncio
import httpx
from typing import Dict
from dotenv import load_dotenv
from backend.src.services.sentiment.base import SentimentAnalyzer
from backend.src.config import config
from backend.src.services.api_logger import APILogger, APICallTimer

# Load environment variables
load_dotenv()


class OpenAIAnalyzer(SentimentAnalyzer):
    """Sentiment analyzer using OpenAI/OpenRouter API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.openai_config = config.sentiment_openai_config
        self.system_prompt = config.sentiment_system_prompt
        
        self._algorithm_id = "openai"
        self._algorithm_version = self.openai_config.get('model', 'unknown')
    
    async def analyze(self, text: str, post_id: str = None) -> Dict:
        """
        Analyze sentiment using OpenRouter API
        
        Args:
            text: Tweet text to analyze
            post_id: Optional post ID for logging
            
        Returns:
            Dict with classification, confidence, algorithm info
        """
        if not self.api_key:
            # Fallback to keyword matching if no API key
            return await self._fallback_keyword_analysis(text)
        
        try:
            # Call OpenRouter API with retries
            result = await self._call_openrouter_with_retry(text, post_id=post_id)
            return result
            
        except Exception as e:
            print(f"   ⚠️ OpenRouter API failed: {e}")
            # Fallback to keyword matching
            return await self._fallback_keyword_analysis(text)
    
    async def _call_openrouter_with_retry(self, text: str, post_id: str = None) -> Dict:
        """Call OpenRouter API with retry logic and logging"""
        max_retries = self.openai_config.get('max_retries', 3)
        timeout = self.openai_config.get('timeout_seconds', 30)
        
        endpoint = self.openai_config.get('api_base_url') + "/chat/completions"
        request_data = {
            "model": self.openai_config.get('model'),
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Analyze this tweet: {text}"}
            ],
            "temperature": self.openai_config.get('temperature', 0.3),
            "max_tokens": self.openai_config.get('max_tokens', 200)
        }
        
        for attempt in range(max_retries):
            try:
                with APICallTimer() as timer:
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.post(
                            endpoint,
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json"
                            },
                            json=request_data
                        )
                        
                        response.raise_for_status()
                        result = response.json()
                
                # Log successful API call
                APILogger.log_api_call(
                    service='openrouter',
                    endpoint=endpoint,
                    request_data=request_data,
                    response_data=result,
                    response_time_ms=timer.elapsed_ms,
                    status='success',
                    context={'post_id': post_id, 'algorithm_id': self.algorithm_id}
                )
                
                # Parse response
                return self._parse_openrouter_response(result)
                    
            except Exception as e:
                # Log failed API call
                APILogger.log_api_call(
                    service='openrouter',
                    endpoint=endpoint,
                    request_data=request_data,
                    response_data=None,
                    response_time_ms=None,
                    status='error' if attempt == max_retries - 1 else 'retry',
                    error_message=str(e),
                    context={'post_id': post_id, 'algorithm_id': self.algorithm_id}
                )
                
                if attempt == max_retries - 1:
                    raise
                # Wait before retry (exponential backoff)
                await asyncio.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
    
    def _parse_openrouter_response(self, response: Dict) -> Dict:
        """Parse OpenRouter API response (expects score 0-100)"""
        try:
            content = response["choices"][0]["message"]["content"]
            
            # Try to parse as JSON
            parsed = json.loads(content)
            
            # Get score (0-100)
            score = float(parsed.get("score", 50))
            score = max(0, min(100, score))  # Clamp to 0-100
            
            # Map score to classification for backward compatibility
            if score < 40:
                classification = "Bearish"
            elif score < 60:
                classification = "Neutral"
            else:
                classification = "Bullish"
            
            # Derive confidence from score distance from neutral (50)
            confidence = abs(score - 50) / 50  # 0.0 to 1.0
            confidence = max(0.5, confidence)  # Minimum 0.5
            
            return {
                "classification": classification,
                "confidence": confidence,
                "score": score,
                "reasoning": parsed.get("reasoning", ""),
                "algorithm_id": self.algorithm_id,
                "algorithm_version": self.algorithm_version
            }
        except Exception as e:
            # If parsing fails, return neutral
            return {
                "classification": "Neutral",
                "confidence": 0.5,
                "score": 50,
                "reasoning": f"Parse error: {str(e)}",
                "algorithm_id": self.algorithm_id,
                "algorithm_version": self.algorithm_version
            }
    
    async def _fallback_keyword_analysis(self, text: str) -> Dict:
        """Fallback keyword-based analysis"""
        text_lower = text.lower()
        
        bullish_keywords = ["moon", "bullish", "buy", "pump", "rocket", "🚀", "up", "gain", "accumulate"]
        bearish_keywords = ["dump", "bearish", "sell", "crash", "down", "loss", "exit"]
        
        bullish_count = sum(1 for kw in bullish_keywords if kw in text_lower)
        bearish_count = sum(1 for kw in bearish_keywords if kw in text_lower)
        
        if bullish_count > bearish_count:
            classification = "Bullish"
            confidence = min(0.6 + (bullish_count * 0.1), 0.95)
            score = 60 + (bullish_count * 10)  # 60-100 range
        elif bearish_count > bullish_count:
            classification = "Bearish"
            confidence = min(0.6 + (bearish_count * 0.1), 0.95)
            score = 40 - (bearish_count * 10)  # 0-40 range
        else:
            classification = "Neutral"
            confidence = 0.5
            score = 50
        
        score = max(0, min(100, score))  # Clamp to 0-100
        
        return {
            "classification": classification,
            "confidence": confidence,
            "score": score,
            "reasoning": "Keyword fallback (API unavailable)",
            "algorithm_id": "keyword-fallback",
            "algorithm_version": "v1.0"
        }
    
    @property
    def algorithm_id(self) -> str:
        return self._algorithm_id
    
    @property
    def algorithm_version(self) -> str:
        return self._algorithm_version
