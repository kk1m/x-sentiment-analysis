"""
Analyze Posts
Run sentiment analysis and bot detection on collected posts
"""
import asyncio
from backend.src.storage.database import get_session
from backend.src.models.post import Post
from backend.src.models.author import Author
from backend.src.models.engagement import Engagement
from backend.src.services.sentiment_service import SentimentService
from backend.src.services.bot_detector import BotDetector
from backend.src.config import config


async def main():
    print("🧠 Analyzing collected posts...")
    print("")
    
    session = get_session()
    
    # Get posts without sentiment scores
    posts = session.query(Post).outerjoin(
        Post.sentiment_scores
    ).filter(
        Post.sentiment_scores == None
    ).limit(20).all()
    
    if not posts:
        print("⚠️  No unanalyzed posts found")
        print("   Run: python collect_small_batch.py")
        return
    
    print(f"Found {len(posts)} posts to analyze")
    print("")
    
    sentiment_service = SentimentService()
    bot_detector = BotDetector()
    
    # Get algorithms from config
    sentiment_algo = config.sentiment_algorithm
    bot_algo = config.bot_detection_algorithm
    
    print(f"Using sentiment algorithm: {sentiment_algo}")
    print(f"Using bot detection algorithm: {bot_algo}")
    print("")
    
    for i, post in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] Analyzing post {post.post_id[:10]}...")
        
        # Sentiment analysis (using config)
        score = await sentiment_service.classify_and_store(
            post_id=post.post_id,
            text=post.text,
            algorithm=sentiment_algo
        )
        
        # Bot detection
        author = session.query(Author).filter_by(user_id=post.author_id).first()
        if author:
            bot_score = bot_detector.calculate_and_store_bot_likelihood(
                post_id=post.post_id,
                author_data={
                    "user_id": author.user_id,
                    "followers_count": author.followers_count,
                    "following_count": author.following_count,
                    "verified": author.verified,
                    "created_at": author.created_at,
                    "profile_description": author.profile_description
                }
            )
            
            print(f"   Sentiment: {score.classification.value} ({score.confidence:.2f})")
            print(f"   Bot score: {bot_score:.2f}")
        
        print("")
    
    session.close()
    
    print("✅ Analysis complete!")
    print("")
    print("📊 Next steps:")
    print("   1. Run: python run_aggregator.py")
    print("   2. Check: curl \"http://localhost:8000/sentiment/trends?topic=Bitcoin&days=1\"")


if __name__ == "__main__":
    asyncio.run(main())
