"""
Weighting Calculator Service
Calculates weighted sentiment scores based on visibility, influence, verification, and bot penalty
"""
import math
from typing import Dict, Optional
from backend.src.models.weighting_config import WeightingConfig


class WeightingCalculator:
    """Calculates weighted sentiment contribution for posts"""
    
    def __init__(self, config: Optional[WeightingConfig] = None):
        """
        Initialize with weighting configuration
        
        Args:
            config: WeightingConfig object (uses default if None)
        """
        if config is None:
            # Use default configuration
            self.config = {
                "version": "v1.0",
                "visibility_weight": lambda engagement: math.log(1 + engagement["like_count"] + engagement["retweet_count"] * 2 + engagement["reply_count"] + engagement["quote_count"]),
                "influence_weight": lambda followers: math.log(1 + followers),
                "verification_multiplier": 1.5,
                "bot_penalty": lambda bot_score: max(0, 1 - bot_score * 2)
            }
        else:
            self.config = self._parse_config(config)
    
    def _parse_config(self, config: WeightingConfig) -> Dict:
        """Parse WeightingConfig model into executable functions"""
        # TODO: Safely evaluate formula strings
        # For now, use default formulas
        return {
            "version": config.version,
            "visibility_weight": lambda engagement: math.log(1 + engagement["like_count"] + engagement["retweet_count"] * 2),
            "influence_weight": lambda followers: math.log(1 + followers),
            "verification_multiplier": config.verification_multiplier,
            "bot_penalty": lambda bot_score: max(0, 1 - bot_score * 2)
        }
    
    def calculate_weight(self, post_data: Dict) -> float:
        """
        Calculate weight for a post
        
        Args:
            post_data: Dict with:
                - engagement: {like_count, retweet_count, reply_count, quote_count}
                - author: {followers_count, verified}
                - bot_score: float 0-1
        
        Returns:
            Weight value (higher = more influence on aggregate sentiment)
        """
        # Visibility weight (engagement metrics)
        engagement = post_data.get("engagement", {})
        visibility_weight = self.config["visibility_weight"](engagement)
        
        # Influence weight (follower count)
        author = post_data.get("author", {})
        followers = author.get("followers_count", 0)
        influence_weight = self.config["influence_weight"](followers)
        
        # Verification multiplier
        verified = author.get("verified", False)
        verification_mult = self.config["verification_multiplier"] if verified else 1.0
        
        # Bot penalty
        bot_score = post_data.get("bot_score", 0.0)
        bot_penalty = self.config["bot_penalty"](bot_score)
        
        # Combined weight
        weight = visibility_weight * influence_weight * verification_mult * bot_penalty
        
        return weight
    
    def calculate_weighted_sentiment(self, posts: list) -> Dict:
        """
        Calculate aggregate weighted sentiment from list of posts
        
        Args:
            posts: List of post dicts with sentiment, engagement, author, bot_score
        
        Returns:
            Dict with weighted_score, dominant_sentiment
        """
        if not posts:
            return {
                "weighted_score": 0.0,
                "dominant_sentiment": "Neutral"
            }
        
        total_weight = 0.0
        bullish_weight = 0.0
        bearish_weight = 0.0
        
        for post in posts:
            weight = self.calculate_weight(post)
            sentiment = post.get("sentiment", "Neutral")
            
            total_weight += weight
            
            if sentiment == "Bullish":
                bullish_weight += weight
            elif sentiment == "Bearish":
                bearish_weight += weight
        
        if total_weight == 0:
            return {
                "weighted_score": 0.0,
                "dominant_sentiment": "Neutral"
            }
        
        # Calculate weighted score (-1 to 1, negative = bearish, positive = bullish)
        weighted_score = (bullish_weight - bearish_weight) / total_weight
        
        # Determine dominant sentiment
        if weighted_score > 0.1:
            dominant_sentiment = "Bullish"
        elif weighted_score < -0.1:
            dominant_sentiment = "Bearish"
        else:
            dominant_sentiment = "Neutral"
        
        return {
            "weighted_score": weighted_score,
            "dominant_sentiment": dominant_sentiment,
            "bullish_weight": bullish_weight,
            "bearish_weight": bearish_weight,
            "total_weight": total_weight
        }
