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
    
    # Get algorithms from config
    sentiment_algo = config.sentiment_algorithm
    bot_algo = config.bot_detection_algorithm
    
    print(f"Using sentiment algorithm: {sentiment_algo}")
    print(f"Using bot detection algorithm: {bot_algo}")
    print("")
    
    # Get all posts and filter by algorithm
    from backend.src.models.sentiment_score import SentimentScore
    from backend.src.models.bot_signal import BotSignal
    
    all_posts = session.query(Post).all()
    posts_to_analyze = []
    
    for post in all_posts:
        # Check if this post already has sentiment from this algorithm
        existing_sentiment = session.query(SentimentScore).filter_by(
            post_id=post.post_id,
            algorithm_id=sentiment_algo
        ).first()
        
        if not existing_sentiment:
            posts_to_analyze.append(post)
    
    if not posts_to_analyze:
        print("⚠️  No posts need analysis with this algorithm")
        print(f"   All posts already analyzed with '{sentiment_algo}'")
        return
    
    print(f"Found {len(posts_to_analyze)} posts to analyze")
    print("")
    
    # Safety limit
    MAX_API_CALLS = config.sentiment_openai_config.get('max_api_calls_per_run', 10)
    if len(posts_to_analyze) > MAX_API_CALLS:
        print(f"⚠️  Limiting to {MAX_API_CALLS} posts (safety limit)")
        posts_to_analyze = posts_to_analyze[:MAX_API_CALLS]
        print("")
    
    sentiment_service = SentimentService()
    bot_detector = BotDetector()
    
    for i, post in enumerate(posts_to_analyze, 1):
        print(f"[{i}/{len(posts_to_analyze)}] Analyzing post {post.post_id[:10]}...")
        
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
