"""
Token Manager
Manages multiple X API tokens and rotates between them when rate limits are hit
"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


class TokenManager:
    """Manages multiple X API bearer tokens with automatic rotation"""
    
    def __init__(self):
        # Load all available tokens
        self.tokens = []
        for i in range(1, 10):  # Support up to 9 tokens
            token = os.getenv(f"X_API_KEY_{i}")
            if token and token != "PLACEHOLDER_FOR_THIRD_TOKEN":
                self.tokens.append({
                    "id": i,
                    "token": token,
                    "rate_limited_until": None,
                    "requests_today": 0,
                    "last_request_date": None
                })
        
        if not self.tokens:
            raise ValueError("No X API tokens found in environment variables")
        
        # Load state from file if exists
        self.state_file = "data/token_state.json"
        self._load_state()
        
        print(f"🔑 Token Manager initialized with {len(self.tokens)} tokens")
    
    def _load_state(self):
        """Load token state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    for token_data in self.tokens:
                        token_id = str(token_data["id"])
                        if token_id in state:
                            token_state = state[token_id]
                            if token_state.get("rate_limited_until"):
                                token_data["rate_limited_until"] = datetime.fromisoformat(token_state["rate_limited_until"])
                            token_data["requests_today"] = token_state.get("requests_today", 0)
                            token_data["last_request_date"] = token_state.get("last_request_date")
            except Exception as e:
                print(f"⚠️  Could not load token state: {e}")
    
    def _save_state(self):
        """Save token state to file"""
        state = {}
        for token_data in self.tokens:
            state[str(token_data["id"])] = {
                "rate_limited_until": token_data["rate_limited_until"].isoformat() if token_data["rate_limited_until"] else None,
                "requests_today": token_data["requests_today"],
                "last_request_date": token_data["last_request_date"]
            }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_active_token(self) -> str:
        """
        Get the currently active token (not rate limited)
        
        Returns:
            Bearer token string
        
        Raises:
            Exception if all tokens are rate limited
        """
        now = datetime.now()
        today = now.date().isoformat()
        
        # Reset daily counters if it's a new day
        for token_data in self.tokens:
            if token_data["last_request_date"] != today:
                token_data["requests_today"] = 0
                token_data["last_request_date"] = today
        
        # Find first available token
        for token_data in self.tokens:
            # Check if rate limit has expired
            if token_data["rate_limited_until"]:
                if now >= token_data["rate_limited_until"]:
                    token_data["rate_limited_until"] = None
                    print(f"✅ Token #{token_data['id']} rate limit expired, now available")
                else:
                    continue  # Still rate limited
            
            # This token is available
            token_data["requests_today"] += 1
            self._save_state()
            
            print(f"🔑 Using Token #{token_data['id']} (requests today: {token_data['requests_today']})")
            return token_data["token"]
        
        # All tokens are rate limited
        next_available = min(
            (t["rate_limited_until"] for t in self.tokens if t["rate_limited_until"]),
            default=None
        )
        
        if next_available:
            wait_time = (next_available - now).total_seconds() / 60
            raise Exception(f"All tokens rate limited. Next available in {wait_time:.0f} minutes")
        else:
            raise Exception("All tokens exhausted for today")
    
    def mark_rate_limited(self, token: str, duration_minutes: int = 15):
        """
        Mark a token as rate limited
        
        Args:
            token: The bearer token that hit rate limit
            duration_minutes: How long to wait before retrying (default 15 min)
        """
        for token_data in self.tokens:
            if token_data["token"] == token:
                token_data["rate_limited_until"] = datetime.now() + timedelta(minutes=duration_minutes)
                self._save_state()
                
                print(f"⏰ Token #{token_data['id']} rate limited until {token_data['rate_limited_until'].strftime('%H:%M:%S')}")
                
                # Try to get next available token
                try:
                    next_token = self.get_active_token()
                    print(f"🔄 Switched to Token #{self._get_token_id(next_token)}")
                except Exception as e:
                    print(f"❌ {e}")
                
                return
    
    def _get_token_id(self, token: str) -> int:
        """Get token ID from token string"""
        for token_data in self.tokens:
            if token_data["token"] == token:
                return token_data["id"]
        return 0
    
    def get_status(self) -> dict:
        """Get status of all tokens"""
        now = datetime.now()
        status = {
            "total_tokens": len(self.tokens),
            "available_tokens": 0,
            "rate_limited_tokens": 0,
            "tokens": []
        }
        
        for token_data in self.tokens:
            is_available = not token_data["rate_limited_until"] or now >= token_data["rate_limited_until"]
            
            if is_available:
                status["available_tokens"] += 1
            else:
                status["rate_limited_tokens"] += 1
            
            status["tokens"].append({
                "id": token_data["id"],
                "available": is_available,
                "requests_today": token_data["requests_today"],
                "rate_limited_until": token_data["rate_limited_until"].isoformat() if token_data["rate_limited_until"] else None
            })
        
        return status
