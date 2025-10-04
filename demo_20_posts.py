"""
Demo Script - 20 Posts
Creates 20 diverse MSTR posts for dashboard testing
"""
import asyncio
import random
from datetime import datetime, timedelta
from backend.src.storage.database import get_session
from backend.src.models.author import Author
from backend.src.models.post import Post
from backend.src.models.engagement import Engagement
from backend.src.services.sentiment_service import SentimentService
from backend.src.services.bot_detector import BotDetector


# Demo post templates
BULLISH_POSTS = [
    "MSTR to the moon! 🚀 Best Bitcoin strategy ever!",
    "$MSTR accumulating more Bitcoin. Bullish AF! 💎🙌",
    "MicroStrategy's Bitcoin treasury is genius. Long MSTR!",
    "MSTR is the future of corporate Bitcoin holdings. Bullish!",
    "Just bought more $MSTR. Bitcoin exposure without custody risk!",
    "Saylor knows what he's doing. MSTR = Bitcoin proxy. Bullish!",
    "MSTR earnings looking great. Bitcoin strategy paying off! 🚀",
    "Best way to get Bitcoin exposure in your portfolio? $MSTR!",
]

BEARISH_POSTS = [
    "MSTR is overvalued. Too much Bitcoin risk on balance sheet.",
    "$MSTR will crash when Bitcoin corrects. Sell now!",
    "MicroStrategy's debt levels are concerning. Bearish on MSTR.",
    "MSTR stock too volatile. Better to just buy Bitcoin directly.",
]

NEUTRAL_POSTS = [
    "MSTR announces Q3 earnings next week. Watching closely.",
    "Interesting MSTR Bitcoin acquisition strategy. Time will tell.",
    "$MSTR trading sideways today. Waiting for catalyst.",
    "MSTR vs direct Bitcoin ownership - pros and cons analysis.",
]

# Demo authors
DEMO_AUTHORS = [
    {"username": "crypto_analyst", "display_name": "Crypto Analyst", "followers": 50000, "verified": True, "age_days": 1200},
    {"username": "mstr_bull", "display_name": "MSTR Bull", "followers": 15000, "verified": False, "age_days": 800},
    {"username": "bitcoin_trader", "display_name": "Bitcoin Trader", "followers": 30000, "verified": True, "age_days": 1500},
    {"username": "stock_watcher", "display_name": "Stock Watcher", "followers": 8000, "verified": False, "age_days": 600},
    {"username": "crypto_news", "display_name": "Crypto News", "followers": 100000, "verified": True, "age_days": 2000},
    {"username": "mstr_investor", "display_name": "MSTR Investor", "followers": 5000, "verified": False, "age_days": 400},
    {"username": "btc_maximalist", "display_name": "BTC Maximalist", "followers": 25000, "verified": False, "age_days": 900},
    {"username": "finance_guru", "display_name": "Finance Guru", "followers": 75000, "verified": True, "age_days": 1800},
]


async def create_demo_data():
    """Create 20 demo posts with variety"""
    print("🚀 Creating 20 demo MSTR posts...")
    print("")
    
    session = get_session()
    
    # Create authors
    print("👥 Creating authors...")
    for i, author_data in enumerate(DEMO_AUTHORS):
        author = Author(
            user_id=f"demo_user_{i+1}",
            username=author_data["username"],
            display_name=author_data["display_name"],
            profile_description=f"Crypto enthusiast | {author_data['display_name']}",
            followers_count=author_data["followers"],
            following_count=random.randint(100, 1000),
            verified=author_data["verified"],
            created_at=datetime.now() - timedelta(days=author_data["age_days"]),
            first_seen=datetime.now(),
            last_updated=datetime.now()
        )
        session.add(author)
    
    session.commit()
    print(f"✓ Created {len(DEMO_AUTHORS)} authors")
    
    # Create 20 posts
    print("\n📝 Creating posts...")
    all_posts = BULLISH_POSTS + BEARISH_POSTS + NEUTRAL_POSTS
    
    sentiment_service = SentimentService()
    bot_detector = BotDetector()
    
    for i in range(20):
        # Pick post text
        post_text = all_posts[i % len(all_posts)]
        
        # Pick random author
        author_idx = i % len(DEMO_AUTHORS)
        author_data = DEMO_AUTHORS[author_idx]
        author_id = f"demo_user_{author_idx+1}"
        
        # Create post
        post_id = f"demo_post_{i+1}"
        created_time = datetime.now() - timedelta(hours=random.randint(1, 72))
        
        post = Post(
            post_id=post_id,
            author_id=author_id,
            text=post_text,
            language="en",
            created_at=created_time,
            has_media=random.choice([True, False]),
            collected_at=datetime.now()
        )
        session.add(post)
        
        # Create engagement (varied levels)
        base_engagement = random.randint(10, 500)
        engagement = Engagement(
            post_id=post_id,
            like_count=base_engagement,
            retweet_count=int(base_engagement * 0.3),
            reply_count=int(base_engagement * 0.1),
            quote_count=int(base_engagement * 0.05)
        )
        session.add(engagement)
        
        session.commit()
        
        # Analyze sentiment
        score = await sentiment_service.classify_and_store(
            post_id=post_id,
            text=post_text,
            algorithm="openai-gpt4"
        )
        
        # Detect bots
        bot_score = bot_detector.calculate_and_store_bot_likelihood(
            post_id=post_id,
            author_data={
                "user_id": author_id,
                "followers_count": author_data["followers"],
                "following_count": random.randint(100, 1000),
                "verified": author_data["verified"],
                "created_at": datetime.now() - timedelta(days=author_data["age_days"]),
                "profile_description": f"Crypto enthusiast"
            }
        )
        
        sentiment_emoji = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "🟡"}
        print(f"[{i+1}/20] {sentiment_emoji.get(score.classification.value, '⚪')} @{author_data['username']}: {post_text[:50]}...")
    
    session.close()
    
    print("\n✅ 20 demo posts created successfully!")
    print("\n📊 Next steps:")
    print("   1. python run_aggregator.py  # Create daily aggregate")
    print("   2. streamlit run dashboard.py  # View dashboard")
    print("   3. Or: curl \"http://localhost:8000/sentiment/trends?topic=Bitcoin&days=1\"")


if __name__ == "__main__":
    asyncio.run(create_demo_data())
