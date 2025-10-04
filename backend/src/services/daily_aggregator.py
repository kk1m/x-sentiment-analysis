"""
Daily Aggregator Service
Creates daily aggregate sentiment records from individual posts
"""
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.storage.database import get_session
from backend.src.models.post import Post
from backend.src.models.sentiment_score import SentimentScore, SentimentClassification
from backend.src.models.engagement import Engagement
from backend.src.models.author import Author
from backend.src.models.bot_signal import BotSignal
from backend.src.models.daily_aggregate import DailyAggregate, Topic, DominantSentiment
from backend.src.services.weighting_calculator import WeightingCalculator


class DailyAggregator:
    """Aggregates daily sentiment data"""
    
    def __init__(self):
        self.weighting_calculator = WeightingCalculator()
    
    async def aggregate_daily_sentiment(
        self,
        target_date: date,
        topic: str,
        algorithm: str = "openai-gpt4"
    ) -> Optional[DailyAggregate]:
        """
        Create daily aggregate for a specific date and topic
        
        Args:
            target_date: Date to aggregate
            topic: Topic (Bitcoin, MSTR, BitcoinTreasuries)
            algorithm: Algorithm to use for sentiment scores
        
        Returns:
            DailyAggregate object or None if no data
        """
        session = get_session()
        
        try:
            # Query posts for this date
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())
            
            posts = session.query(Post).filter(
                Post.created_at >= start_datetime,
                Post.created_at <= end_datetime
            ).all()
            
            if not posts:
                return None
            
            # Collect post data with all needed info
            post_data_list = []
            
            bullish_count = 0
            bearish_count = 0
            neutral_count = 0
            total_likes = 0
            total_retweets = 0
            unique_authors = set()
            verified_authors = set()
            bot_flagged = 0
            high_confidence = 0
            
            for post in posts:
                # Get sentiment score
                sentiment_score = session.query(SentimentScore).filter(
                    SentimentScore.post_id == post.post_id,
                    SentimentScore.algorithm_id == algorithm
                ).first()
                
                if not sentiment_score:
                    continue
                
                # Get engagement
                engagement = session.query(Engagement).filter(
                    Engagement.post_id == post.post_id
                ).first()
                
                # Get author
                author = session.query(Author).filter(
                    Author.user_id == post.author_id
                ).first()
                
                # Get bot signal
                bot_signal = session.query(BotSignal).filter(
                    BotSignal.post_id == post.post_id
                ).first()
                
                if not engagement or not author:
                    continue
                
                # Count metrics
                if sentiment_score.classification == SentimentClassification.BULLISH:
                    bullish_count += 1
                elif sentiment_score.classification == SentimentClassification.BEARISH:
                    bearish_count += 1
                else:
                    neutral_count += 1
                
                total_likes += engagement.like_count
                total_retweets += engagement.retweet_count
                
                unique_authors.add(author.user_id)
                if author.verified:
                    verified_authors.add(author.user_id)
                
                if bot_signal and bot_signal.is_likely_bot:
                    bot_flagged += 1
                
                if sentiment_score.is_high_confidence:
                    high_confidence += 1
                
                # Prepare data for weighting
                post_data_list.append({
                    "sentiment": sentiment_score.classification.value,
                    "confidence": sentiment_score.confidence,
                    "engagement": {
                        "like_count": engagement.like_count,
                        "retweet_count": engagement.retweet_count,
                        "reply_count": engagement.reply_count,
                        "quote_count": engagement.quote_count
                    },
                    "author": {
                        "followers_count": author.followers_count,
                        "verified": author.verified
                    },
                    "bot_score": bot_signal.score if bot_signal else 0.0
                })
            
            if not post_data_list:
                return None
            
            # Calculate weighted sentiment
            weighted_result = self.weighting_calculator.calculate_weighted_sentiment(post_data_list)
            
            # Map dominant sentiment to enum
            dominant_map = {
                "Bullish": DominantSentiment.BULLISH,
                "Bearish": DominantSentiment.BEARISH,
                "Neutral": DominantSentiment.NEUTRAL
            }
            
            # Map topic to enum
            topic_map = {
                "Bitcoin": Topic.BITCOIN,
                "MSTR": Topic.MSTR,
                "BitcoinTreasuries": Topic.BITCOIN_TREASURIES
            }
            
            total_posts = len(post_data_list)
            
            # Create aggregate
            aggregate = DailyAggregate(
                date=target_date,
                topic=topic_map.get(topic, Topic.BITCOIN),
                algorithm_id=algorithm,
                total_posts=total_posts,
                total_posts_after_bot_filter=total_posts - bot_flagged,
                unique_authors=len(unique_authors),
                verified_authors=len(verified_authors),
                bullish_count=bullish_count,
                bearish_count=bearish_count,
                neutral_count=neutral_count,
                weighted_score=weighted_result["weighted_score"],
                weighted_bullish_score=weighted_result.get("bullish_weight", 0.0),
                weighted_bearish_score=weighted_result.get("bearish_weight", 0.0),
                dominant_sentiment=dominant_map[weighted_result["dominant_sentiment"]],
                total_likes=total_likes,
                total_retweets=total_retweets,
                avg_engagement_per_post=(total_likes + total_retweets) / total_posts if total_posts > 0 else 0,
                bot_detection_rate=(bot_flagged / total_posts * 100) if total_posts > 0 else 0,
                high_confidence_sentiment_pct=(high_confidence / total_posts * 100) if total_posts > 0 else 0,
                weighting_config_version="v1.0"
            )
            
            session.add(aggregate)
            session.commit()
            session.refresh(aggregate)
            
            return aggregate
            
        finally:
            session.close()
