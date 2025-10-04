"""
Collect Small Batch
Collects a small number of tweets (respects free tier limits)
"""
import asyncio
from datetime import datetime, timedelta
from backend.src.services.x_api_client import XAPIClient
from backend.src.services.post_collector import PostCollector


async def main():
    print("🔍 Collecting small batch of Bitcoin tweets...")
    print("   (Free tier: max 10 tweets per request)")
    print("")
    
    try:
        collector = PostCollector()
        
        # Collect just last 2 hours to stay within limits
        since = datetime.utcnow() - timedelta(hours=2)
        
        posts_stored = await collector.collect_and_store_daily_posts(
            hashtags=["#Bitcoin"],
            since=since,
            batch_job_id=None
        )
        
        print(f"✅ Collected and stored {posts_stored} posts")
        print("")
        print("📊 Now run sentiment analysis:")
        print("   python analyze_posts.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("")
        if "rate limit" in str(e).lower():
            print("⚠️  Rate limit hit. Free tier allows:")
            print("   - 500 tweets/month")
            print("   - ~16 tweets/day")
            print("   - Wait 15 minutes and try again")


if __name__ == "__main__":
    asyncio.run(main())
