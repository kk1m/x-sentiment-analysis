"""
Bot Detector Service
Calculates bot likelihood score based on author patterns
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict
from backend.src.storage.database import get_session
from backend.src.models.bot_signal import BotSignal


class BotDetector:
    """Detects bot-like behavior in X accounts"""
    
    def calculate_bot_likelihood(self, author_data: Dict) -> float:
        """
        Calculate bot likelihood score (0 = human, 1 = bot)
        
        Args:
            author_data: Dict with user info (followers_count, following_count, verified, created_at, etc.)
        
        Returns:
            Bot likelihood score 0.0-1.0
        """
        score = 0.0
        signals = {}
        
        # Signal 1: Account age (newer = more likely bot)
        if "created_at" in author_data:
            if isinstance(author_data["created_at"], str):
                created_at = datetime.fromisoformat(author_data["created_at"].replace("Z", "+00:00"))
            else:
                created_at = author_data["created_at"]
            
            account_age_days = (datetime.now(created_at.tzinfo) - created_at).days
            
            if account_age_days < 30:
                score += 0.3
                signals["account_age_days"] = account_age_days
            elif account_age_days < 90:
                score += 0.15
                signals["account_age_days"] = account_age_days
        
        # Signal 2: Follower/following ratio (high following, low followers = bot)
        followers = author_data.get("followers_count", 0)
        following = author_data.get("following_count", 0)
        
        if following > 0:
            ratio = followers / following
            if ratio < 0.1:  # Following 10x more than followers
                score += 0.25
                signals["follower_ratio"] = ratio
            elif ratio < 0.5:
                score += 0.1
                signals["follower_ratio"] = ratio
        
        # Signal 3: Empty or generic profile
        description = author_data.get("profile_description", "")
        if not description or len(description) < 20:
            score += 0.15
            signals["empty_profile"] = True
        
        # Signal 4: Verification (verified = less likely bot)
        if author_data.get("verified", False):
            score -= 0.2  # Reduce score for verified accounts
            signals["verified"] = True
        
        # Signal 5: Username patterns (numbers, random chars)
        username = author_data.get("username", "")
        if any(char.isdigit() for char in username):
            digit_count = sum(1 for char in username if char.isdigit())
            if digit_count > 4:
                score += 0.1
                signals["username_digits"] = digit_count
        
        # Clamp score to 0-1
        score = max(0.0, min(1.0, score))
        
        return score
    
    def calculate_and_store_bot_likelihood(
        self,
        post_id: str,
        author_data: Dict
    ) -> float:
        """
        Calculate bot likelihood and store in database
        
        Args:
            post_id: Post ID
            author_data: Author information
        
        Returns:
            Bot likelihood score
        """
        score = self.calculate_bot_likelihood(author_data)
        
        session = get_session()
        try:
            bot_signal = BotSignal(
                id=str(uuid.uuid4()),
                post_id=post_id,
                score=score,
                inputs={},  # Could store signals here
                created_at=datetime.utcnow(),
                detector_version="v1.0"
            )
            session.add(bot_signal)
            session.commit()
            return score
        finally:
            session.close()
