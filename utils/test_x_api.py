"""
Test X API Connection
Quick test to verify API credentials work
"""
import asyncio
from backend.src.services.x_api_client import XAPIClient
from datetime import datetime, timedelta


async def test_connection():
    print("🔌 Testing X API connection...")
    print("")
    
    try:
        client = XAPIClient()
        print("✓ API client initialized")
        print(f"  Bearer token: {client.bearer_token[:20]}...")
        print("")
        
        # Test search for Bitcoin tweets
        print("🔍 Searching for recent #Bitcoin tweets...")
        
        since = datetime.utcnow() - timedelta(hours=1)
        result = await client.search_recent(
            query="#Bitcoin",
            max_results=10,
            since=since
        )
        
        posts = result.get("data", [])
        users = result.get("includes", {}).get("users", [])
        
        print(f"✓ API call successful!")
        print(f"  Found {len(posts)} tweets in the last hour")
        print("")
        
        if posts:
            print("📝 Sample tweets:")
            for i, post in enumerate(posts[:3], 1):
                text = post["text"][:80] + "..." if len(post["text"]) > 80 else post["text"]
                print(f"  {i}. {text}")
                print(f"     Likes: {post.get('public_metrics', {}).get('like_count', 0)}, "
                      f"Retweets: {post.get('public_metrics', {}).get('retweet_count', 0)}")
            print("")
        
        print("🎉 X API connection successful!")
        print("")
        print("Next steps:")
        print("  1. Run: python -c 'import asyncio; from backend.src.jobs.daily_batch import run_daily_batch; asyncio.run(run_daily_batch())'")
        print("  2. Run: python run_aggregator.py")
        print("  3. Check: curl \"http://localhost:8000/sentiment/trends?topic=Bitcoin&days=1\"")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("")
        print("Troubleshooting:")
        print("  - Check your Bearer Token in .env")
        print("  - Verify you have API access at https://developer.twitter.com/")
        print("  - Make sure you're on the Free tier (500 tweets/month)")


if __name__ == "__main__":
    asyncio.run(test_connection())
