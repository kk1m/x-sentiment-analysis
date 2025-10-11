"""
Demo Script - Quarterly Time Series
Creates 3 months of MSTR posts following Mon/Wed/Fri/Sun schedule
Simulates realistic sentiment fluctuations and bot influence
"""
import asyncio
import random
from datetime import datetime, timedelta, date
from backend.src.storage.database import get_session
from backend.src.models.author import Author
from backend.src.models.post import Post
from backend.src.models.engagement import Engagement
from backend.src.services.sentiment_service import SentimentService
from backend.src.services.bot_detector import BotDetector


# Realistic MSTR sentiment patterns (simulating Bitcoin correlation)
# Week 1-4: Bull run (70% bullish)
# Week 5-8: Consolidation (50% bullish)
# Week 9-10: Correction (30% bullish)
# Week 11-13: Recovery (60% bullish)

def get_sentiment_bias_for_week(week_num):
    """Get bullish probability for a given week"""
    if week_num <= 4:
        return 0.70  # Bull run
    elif week_num <= 8:
        return 0.50  # Consolidation
    elif week_num <= 10:
        return 0.30  # Correction
    else:
        return 0.60  # Recovery


# Post templates
BULLISH_POSTS = [
    "MSTR to the moon! 🚀 Best Bitcoin strategy ever!",
    "$MSTR accumulating more Bitcoin. Bullish AF! 💎🙌",
    "MicroStrategy's Bitcoin treasury is genius. Long MSTR!",
    "MSTR is the future of corporate Bitcoin holdings. Bullish!",
    "Just bought more $MSTR. Bitcoin exposure without custody risk!",
    "Saylor knows what he's doing. MSTR = Bitcoin proxy. Bullish!",
    "MSTR earnings looking great. Bitcoin strategy paying off! 🚀",
    "Best way to get Bitcoin exposure in your portfolio? $MSTR!",
    "MSTR breaking out! New all-time highs incoming! 🚀",
    "Loaded up on more $MSTR. This is the way! 💎",
]

BEARISH_POSTS = [
    "MSTR is overvalued. Too much Bitcoin risk on balance sheet.",
    "$MSTR will crash when Bitcoin corrects. Sell now!",
    "MicroStrategy's debt levels are concerning. Bearish on MSTR.",
    "MSTR stock too volatile. Better to just buy Bitcoin directly.",
    "Selling my $MSTR position. Risk/reward not favorable.",
    "MSTR down 15% this week. Told you it was overvalued.",
    "MicroStrategy's leverage is dangerous. Bearish.",
]

NEUTRAL_POSTS = [
    "MSTR announces Q3 earnings next week. Watching closely.",
    "Interesting MSTR Bitcoin acquisition strategy. Time will tell.",
    "$MSTR trading sideways today. Waiting for catalyst.",
    "MSTR vs direct Bitcoin ownership - pros and cons analysis.",
    "Analyzing MSTR's latest Bitcoin purchase. Mixed feelings.",
]

# Human authors (legitimate accounts)
HUMAN_AUTHORS = [
    {"username": "crypto_analyst", "display_name": "Crypto Analyst", "followers": 50000, "verified": True, "age_days": 1200, "bot_score": 0.05},
    {"username": "mstr_bull", "display_name": "MSTR Bull", "followers": 15000, "verified": False, "age_days": 800, "bot_score": 0.15},
    {"username": "bitcoin_trader", "display_name": "Bitcoin Trader", "followers": 30000, "verified": True, "age_days": 1500, "bot_score": 0.08},
    {"username": "stock_watcher", "display_name": "Stock Watcher", "followers": 8000, "verified": False, "age_days": 600, "bot_score": 0.20},
    {"username": "crypto_news", "display_name": "Crypto News", "followers": 100000, "verified": True, "age_days": 2000, "bot_score": 0.10},
    {"username": "mstr_investor", "display_name": "MSTR Investor", "followers": 5000, "verified": False, "age_days": 400, "bot_score": 0.25},
]

# Bot authors (suspicious accounts - always bullish to skew sentiment)
BOT_AUTHORS = [
    {"username": "crypto_moon_2024", "display_name": "Crypto Moon", "followers": 100, "verified": False, "age_days": 30, "bot_score": 0.85},
    {"username": "btc_pumper_x", "display_name": "BTC Pumper", "followers": 50, "verified": False, "age_days": 15, "bot_score": 0.90},
    {"username": "mstr_to_moon_bot", "display_name": "MSTR Moon Bot", "followers": 200, "verified": False, "age_days": 45, "bot_score": 0.80},
    {"username": "crypto_gains_247", "display_name": "Crypto Gains 24/7", "followers": 75, "verified": False, "age_days": 20, "bot_score": 0.88},
]

BOT_POSTS = [
    "MSTR 🚀🚀🚀 TO THE MOON!!! BUY NOW!!! 💎💎💎",
    "$MSTR PUMPING!!! 1000% GAINS INCOMING!!! 🚀🚀🚀",
    "MSTR IS THE BEST INVESTMENT EVER!!! BUY BUY BUY!!!",
    "🚀🚀🚀 MSTR MOON MISSION!!! DON'T MISS OUT!!! 💎💎💎",
]


async def create_quarterly_data():
    """Create 3 months of data following Mon/Wed/Fri/Sun schedule"""
    print("🚀 Creating quarterly time series data...")
    print("   Schedule: Mon/Wed/Fri/Sun (4x per week)")
    print("   Duration: Last 90 days (3 months)")
    print("")
    
    session = get_session()
    
    # Create all authors (human + bot)
    print("👥 Creating authors...")
    all_authors = HUMAN_AUTHORS + BOT_AUTHORS
    
    for i, author_data in enumerate(all_authors):
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
    print(f"✓ Created {len(all_authors)} authors ({len(HUMAN_AUTHORS)} human, {len(BOT_AUTHORS)} bots)")
    
    # Generate collection dates (Mon/Wed/Fri/Sun for last 90 days)
    print("\n📅 Generating collection schedule...")
    collection_dates = []
    start_date = datetime.now() - timedelta(days=90)
    
    for day_offset in range(90):
        check_date = start_date + timedelta(days=day_offset)
        # Mon=0, Wed=2, Fri=4, Sun=6
        if check_date.weekday() in [0, 2, 4, 6]:
            collection_dates.append(check_date)
    
    print(f"✓ Generated {len(collection_dates)} collection dates")
    
    # Create posts for each collection date
    print(f"\n📝 Creating posts for {len(collection_dates)} collection days...")
    print("   (5 posts per day)")
    print("")
    
    sentiment_service = SentimentService()
    bot_detector = BotDetector()
    
    post_counter = 0
    
    for collection_idx, collection_date in enumerate(collection_dates):
        week_num = (collection_date - start_date).days // 7 + 1
        bullish_bias = get_sentiment_bias_for_week(week_num)
        
        # Collect 5 posts for this day
        for post_idx in range(5):
            post_counter += 1
            
            # Decide if this post is from bot or human
            # Bots are 30% of posts and always bullish (to skew sentiment)
            is_bot_post = random.random() < 0.30
            
            if is_bot_post:
                # Bot post (always bullish)
                author_idx = random.randint(0, len(BOT_AUTHORS) - 1) + len(HUMAN_AUTHORS)
                post_text = random.choice(BOT_POSTS)
                sentiment_override = "Bullish"
            else:
                # Human post (follows market sentiment)
                author_idx = random.randint(0, len(HUMAN_AUTHORS) - 1)
                
                # Determine sentiment based on weekly bias
                rand = random.random()
                if rand < bullish_bias:
                    post_text = random.choice(BULLISH_POSTS)
                    sentiment_override = "Bullish"
                elif rand < bullish_bias + (1 - bullish_bias) * 0.6:
                    post_text = random.choice(BEARISH_POSTS)
                    sentiment_override = "Bearish"
                else:
                    post_text = random.choice(NEUTRAL_POSTS)
                    sentiment_override = "Neutral"
            
            author_data = all_authors[author_idx]
            author_id = f"demo_user_{author_idx+1}"
            post_id = f"demo_post_{post_counter}"
            
            # Create post with timestamp on collection date
            post_time = collection_date + timedelta(hours=random.randint(0, 23))
            
            post = Post(
                post_id=post_id,
                author_id=author_id,
                text=post_text,
                language="en",
                created_at=post_time,
                has_media=random.choice([True, False]),
                collected_at=collection_date
            )
            session.add(post)
            
            # Create engagement (bots get low engagement, humans vary)
            if is_bot_post:
                base_engagement = random.randint(5, 20)  # Bots get low engagement
            else:
                base_engagement = random.randint(50, 500)  # Humans get varied engagement
            
            engagement = Engagement(
                post_id=post_id,
                like_count=base_engagement,
                retweet_count=int(base_engagement * 0.3),
                reply_count=int(base_engagement * 0.1),
                quote_count=int(base_engagement * 0.05)
            )
            session.add(engagement)
            
            session.commit()
            
            # Analyze sentiment (use override for consistency)
            score = await sentiment_service.classify_and_store(
                post_id=post_id,
                text=post_text,
                algorithm="openai-gpt4"
            )
            
            # Detect bots (use predefined scores)
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
        
        # Progress indicator
        if (collection_idx + 1) % 10 == 0:
            print(f"✓ Processed {collection_idx + 1}/{len(collection_dates)} collection days ({post_counter} posts)")
    
    session.close()
    
    print(f"\n✅ Created {post_counter} posts across {len(collection_dates)} collection days!")
    print(f"   Date range: {collection_dates[0].date()} to {collection_dates[-1].date()}")
    print(f"   Schedule: Mon/Wed/Fri/Sun")
    print(f"   Human posts: ~{int(post_counter * 0.7)}")
    print(f"   Bot posts: ~{int(post_counter * 0.3)} (always bullish to skew sentiment)")
    print("")
    print("📊 Next steps:")
    print("   1. python run_aggregator_bulk.py  # Aggregate all days")
    print("   2. streamlit run dashboard.py  # View dashboard with 3-month trends")


if __name__ == "__main__":
    asyncio.run(create_quarterly_data())
