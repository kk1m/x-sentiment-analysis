"""
Collect Small Batch
Collects a small number of tweets (respects free tier limits)
"""
import asyncio
import csv
import os
from datetime import datetime, timedelta
from backend.src.services.x_api_client import XAPIClient
from backend.src.services.post_collector import PostCollector


def log_collection(posts_count, status="success", error_msg=None):
    """Log collection attempt to CSV"""
    log_file = "collection_log.csv"
    
    # Create file with headers if doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "date", "day_of_week", "status", "posts_collected", "error"])
    
    # Append this collection
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        now = datetime.now()
        writer.writerow([
            now.strftime("%Y-%m-%d %H:%M:%S"),
            now.strftime("%Y-%m-%d"),
            now.strftime("%A"),
            status,
            posts_count,
            error_msg or ""
        ])


async def main():
    print("🔍 Collecting small batch of MSTR tweets...")
    print("   (Free tier: collecting 10 tweets)")
    print("")
    
    # Build custom query with spam filters
    hashtag = "#MSTR"
    
    # Context keywords to ensure tweet is actually about MSTR/Bitcoin/crypto
    context_keywords = "(STRC OR STRK OR MicroStrategy OR Saylor OR Bitcoin OR BTC OR crypto OR cryptocurrency OR blockchain OR price OR market OR trading OR investment OR bullish OR bearish OR buy OR sell OR hodl OR rally OR dump OR pump OR crash OR moon OR dip OR ATH OR halving OR mining OR wallet OR exchange OR volatility OR adoption OR institutional OR treasury OR strategy OR holdings OR accumulation OR correlation OR technical OR fundamental OR analysis OR sentiment OR trend OR breakout OR support OR resistance OR stock OR shares OR equity OR nasdaq)"
    
    # Quality filters
    filters = [
        "-is:retweet",           # No retweets
        "-is:reply",             # No replies (focus on original thoughts)
        "min_retweets:1",        # At least 1 retweet (some engagement)
        "min_faves:2",           # At least 2 likes (filters spam)
        "lang:en"                # English only
    ]
    
    # Build full query
    query = f"{hashtag} {context_keywords} {' '.join(filters)}"
    
    print(f"📝 Query: {query[:100]}...")
    print("")
    
    try:
        from backend.src.services.x_api_client import XAPIClient
        from backend.src.storage.database import get_session
        from backend.src.models.author import Author
        from backend.src.models.post import Post
        from backend.src.models.engagement import Engagement
        
        x_client = XAPIClient()
        
        # Collect just last 2 hours to stay within limits
        since = datetime.utcnow() - timedelta(hours=2)
        
        # Use direct query search
        response = await x_client.search_by_query(
            query=query,
            max_results=10,
            since=since
        )
        
        # Store posts manually
        posts_data = response.get("data", [])
        users_data = response.get("includes", {}).get("users", [])
        
        if not posts_data:
            print("⚠️  No posts found matching query")
            return
        
        users_by_id = {user["id"]: user for user in users_data}
        session = get_session()
        posts_stored = 0
        
        for post_data in posts_data:
            author_id = post_data["author_id"]
            user_data = users_by_id.get(author_id)
            
            if not user_data:
                continue
            
            # Get or create author
            author = session.query(Author).filter_by(user_id=author_id).first()
            if not author:
                author = Author(
                    user_id=user_data["id"],
                    username=user_data["username"],
                    display_name=user_data["name"],
                    profile_description=user_data.get("description", ""),
                    followers_count=user_data["public_metrics"]["followers_count"],
                    following_count=user_data["public_metrics"]["following_count"],
                    verified=user_data.get("verified", False),
                    created_at=datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00")),
                    first_seen=datetime.utcnow(),
                    last_updated=datetime.utcnow()
                )
                session.add(author)
                session.flush()
            else:
                author.followers_count = user_data["public_metrics"]["followers_count"]
                author.following_count = user_data["public_metrics"]["following_count"]
                author.last_updated = datetime.utcnow()
            
            # Check if post exists
            existing_post = session.query(Post).filter_by(post_id=post_data["id"]).first()
            if existing_post:
                continue
            
            # Create post
            post = Post(
                post_id=post_data["id"],
                author_id=author_id,
                batch_job_id=None,
                text=post_data["text"],
                language=post_data.get("lang"),
                created_at=datetime.fromisoformat(post_data["created_at"].replace("Z", "+00:00")),
                has_media=False,
                collected_at=datetime.utcnow()
            )
            session.add(post)
            
            # Create engagement
            metrics = post_data.get("public_metrics", {})
            engagement = Engagement(
                post_id=post_data["id"],
                like_count=metrics.get("like_count", 0),
                retweet_count=metrics.get("retweet_count", 0),
                reply_count=metrics.get("reply_count", 0),
                quote_count=metrics.get("quote_count", 0)
            )
            session.add(engagement)
            posts_stored += 1
        
        session.commit()
        session.close()
        
        # Log success
        log_collection(posts_stored, status="success")
        
        print(f"✅ Collected and stored {posts_stored} posts")
        print("")
        print("📊 Now run sentiment analysis:")
        print("   python analyze_posts.py")
        
    except Exception as e:
        # Log failure
        error_type = "rate_limit" if "rate limit" in str(e).lower() else "error"
        log_collection(0, status=error_type, error_msg=str(e))
        
        print(f"❌ Error: {e}")
        print("")
        if "rate limit" in str(e).lower():
            print("⚠️  Rate limit hit. Free tier allows:")
            print("   - 500 tweets/month")
            print("   - ~16 tweets/day")
            print("   - Wait 15 minutes and try again")


if __name__ == "__main__":
    asyncio.run(main())
