"""
X API Client
Wrapper for X (Twitter) API v2 using httpx with automatic token rotation
"""
import httpx
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from backend.src.services.token_manager import TokenManager

load_dotenv()


class RateLimitError(Exception):
    """Raised when X API rate limit is exceeded"""
    pass


class XAPIClient:
    """Client for X API v2 with automatic token rotation"""
    
    def __init__(self):
        # Use token manager for automatic rotation
        try:
            self.token_manager = TokenManager()
            self.bearer_token = self.token_manager.get_active_token()
        except Exception as e:
            # Fallback to single token if manager fails
            print(f"⚠️  Token manager failed, using fallback: {e}")
            self.token_manager = None
            self.bearer_token = os.getenv("X_API_KEY")
            if not self.bearer_token:
                raise ValueError("X_API_KEY not found in environment variables")
        
        self.base_url = "https://api.twitter.com/2"
        self._update_headers()
    
    def _update_headers(self):
        """Update headers with current bearer token"""
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
    
    async def search_recent(
        self,
        query: str,
        max_results: int = 10,
        since: Optional[datetime] = None
    ) -> Dict:
        """
        Search recent tweets matching query
        
        Args:
            query: Search query (e.g., "#Bitcoin OR #BTC")
            max_results: Max tweets to return (10-100)
            since: Only tweets after this datetime
        
        Returns:
            Dict with 'data' (tweets) and 'includes' (users)
        """
        params = {
            "query": query,
            "max_results": min(max_results, 10),
            "sort_order": "relevancy",  # Sort by engagement/relevance instead of recency
            "tweet.fields": "created_at,author_id,public_metrics,lang",
            "expansions": "author_id",
            "user.fields": "username,name,verified,public_metrics,created_at,description"
        }
        
        if since:
            params["start_time"] = since.isoformat() + "Z"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/tweets/search/recent",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 429:
                    # Mark current token as rate limited and try to rotate
                    if self.token_manager:
                        self.token_manager.mark_rate_limited(self.bearer_token, duration_minutes=60)
                        # Try with next token
                        try:
                            self.bearer_token = self.token_manager.get_active_token()
                            self._update_headers()
                            # Retry request with new token
                            response = await client.get(
                                f"{self.base_url}/tweets/search/recent",
                                headers=self.headers,
                                params=params,
                                timeout=30.0
                            )
                            if response.status_code == 429:
                                raise RateLimitError("X API rate limit exceeded")
                        except Exception:
                            raise RateLimitError("X API rate limit exceeded")
                    else:
                        raise RateLimitError("X API rate limit exceeded")
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    if self.token_manager:
                        self.token_manager.mark_rate_limited(self.bearer_token, duration_minutes=60)
                    raise RateLimitError("X API rate limit exceeded")
                # Print error details for debugging
                print(f"Error response: {e.response.text}")
                raise
    
    async def search_by_query(
        self,
        query: str,
        max_results: int = 10,
        since: Optional[datetime] = None
    ) -> Dict:
        """
        Search tweets by custom query string
        
        Args:
            query: Full X API query string (e.g., "#MSTR (Bitcoin OR crypto) -is:retweet")
            max_results: Max tweets to return
            since: Only tweets after this datetime
        
        Returns:
            Dict with 'data' (tweets) and 'includes' (users)
        """
        return await self.search_recent(query, max_results, since)
