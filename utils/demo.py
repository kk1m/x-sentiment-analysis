"""
Demo Script
Shows the X Sentiment Analysis system in action
"""
import asyncio
from datetime import datetime, timedelta
from backend.src.storage.database import get_session
from backend.src.models.author import Author
from backend.src.models.post import Post
from backend.src.models.engagement import Engagement
from backend.src.services.sentiment_service import SentimentService
from backend.src.services.bot_detector import BotDetector


async def create_demo_data():
    """Create some demo data to test the system"""
    print("🚀 Creating demo data...")
    
    session = get_session()
    
    # Create demo authors
    author1 = Author(
        user_id="demo_user_1",
        username="crypto_bull",
        display_name="Crypto Bull",
        profile_description="Bitcoin maximalist",
        followers_count=10000,
        following_count=500,
        verified=True,
        created_at=datetime.now() - timedelta(days=365),
        first_seen=datetime.now(),
        last_updated=datetime.now()
    )
    
    author2 = Author(
        user_id="demo_user_2",
        username="bitcoin_bear",
        display_name="Bitcoin Bear",
        profile_description="Crypto skeptic",
        followers_count=5000,
        following_count=300,
        verified=False,
        created_at=datetime.now() - timedelta(days=180),
        first_seen=datetime.now(),
        last_updated=datetime.now()
    )
    
    session.add(author1)
    session.add(author2)
    
    # Create demo posts
    post1 = Post(
        post_id="demo_post_1",
        author_id="demo_user_1",
        text="Bitcoin to the moon! 🚀 $100k incoming! Bullish!",
        language="en",
        created_at=datetime.now() - timedelta(hours=2),
        has_media=False,
        collected_at=datetime.now()
    )
    
    post2 = Post(
        post_id="demo_post_2",
        author_id="demo_user_2",
        text="Bitcoin crash incoming. Sell everything. Bearish market.",
        language="en",
        created_at=datetime.now() - timedelta(hours=1),
        has_media=False,
        collected_at=datetime.now()
    )
    
    session.add(post1)
    session.add(post2)
    
    # Create engagement
    eng1 = Engagement(
        post_id="demo_post_1",
        like_count=100,
        retweet_count=50,
        reply_count=20,
        quote_count=10
    )
    
    eng2 = Engagement(
        post_id="demo_post_2",
        like_count=10,
        retweet_count=5,
        reply_count=2,
        quote_count=1
    )
    
    session.add(eng1)
    session.add(eng2)
    
    session.commit()
    print("✓ Demo authors and posts created")
    
    # Analyze sentiment
    print("\n📊 Analyzing sentiment...")
    sentiment_service = SentimentService()
    
    score1 = await sentiment_service.classify_and_store(
        post_id="demo_post_1",
        text=post1.text,
        algorithm="openai-gpt4"
    )
    print(f"  Post 1: {score1.classification.value} (confidence: {score1.confidence:.2f})")
    
    score2 = await sentiment_service.classify_and_store(
        post_id="demo_post_2",
        text=post2.text,
        algorithm="openai-gpt4"
    )
    print(f"  Post 2: {score2.classification.value} (confidence: {score2.confidence:.2f})")
    
    # Detect bots
    print("\n🤖 Detecting bots...")
    bot_detector = BotDetector()
    
    bot_score1 = bot_detector.calculate_and_store_bot_likelihood(
        post_id="demo_post_1",
        author_data={
            "user_id": "demo_user_1",
            "followers_count": 10000,
            "following_count": 500,
            "verified": True,
            "created_at": datetime.now() - timedelta(days=365),
            "profile_description": "Bitcoin maximalist"
        }
    )
    print(f"  Author 1 bot score: {bot_score1:.2f} ({'likely human' if bot_score1 < 0.3 else 'uncertain'})")
    
    bot_score2 = bot_detector.calculate_and_store_bot_likelihood(
        post_id="demo_post_2",
        author_data={
            "user_id": "demo_user_2",
            "followers_count": 5000,
            "following_count": 300,
            "verified": False,
            "created_at": datetime.now() - timedelta(days=180),
            "profile_description": "Crypto skeptic"
        }
    )
    print(f"  Author 2 bot score: {bot_score2:.2f} ({'likely human' if bot_score2 < 0.3 else 'uncertain'})")
    
    session.close()
    
    print("\n✅ Demo data created successfully!")
    print("\n📡 Start the API server:")
    print("   uvicorn backend.src.main:app --reload")
    print("\n🌐 Then visit:")
    print("   http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(create_demo_data())
