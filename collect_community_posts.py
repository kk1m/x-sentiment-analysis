"""
Collect Community Posts
Collects top 5 posts from "Irresponsibly Long $MSTR" community
Run on: Monday, Wednesday, Friday, Sunday
"""
import asyncio
import json
import os
import csv
from datetime import datetime, timedelta
from backend.src.services.x_api_client import XAPIClient
from backend.src.storage.database import get_session
from backend.src.models.author import Author
from backend.src.models.post import Post
from backend.src.models.engagement import Engagement


async def collect_community_posts():
    """Collect top 5 posts from the community"""
    
    print("🎯 Collecting posts from 'Irresponsibly Long $MSTR' community...")
    print("")
    
    # Load community ID
    if not os.path.exists("community_config.json"):
        print("❌ Error: community_config.json not found")
        print("   Run: python find_community.py first")
        return
    
    with open("community_config.json", "r") as f:
        config = json.load(f)
    
    community_id = config["community_id"]
    community_name = config["community_name"]
    
    print(f"📍 Community: {community_name}")
    print(f"   ID: {community_id}")
    print("")
    
    # Collect posts
    try:
        client = XAPIClient()
        
        # Query: posts from community, with quality filter
        # NOTE: context: operator not available on free tier (400 error)
        # Fallback: search for posts mentioning "Irresponsibly Long" + MSTR
        # This captures posts from community members using their signature phrase
        query = '"Irresponsibly Long" ($MSTR OR MicroStrategy) min_retweets:2 -is:retweet lang:en'
        
        # Time window: last 72 hours (since last collection)
        # Mon->Wed = 48h, Wed->Fri = 48h, Fri->Sun = 48h, Sun->Mon = 48h
        # Using 72h as buffer
        since = datetime.utcnow() - timedelta(hours=72)
        
        print(f"🔍 Query: {query}")
        print(f"   Time window: Last 72 hours")
        print(f"   Collecting top 5 posts by engagement...")
        print("")
        
        response = await client.search_recent(
            query=query,
            max_results=5,
            since=since
        )
        
        posts_data = response.get("data", [])
        users_data = response.get("includes", {}).get("users", [])
        
        if not posts_data:
            print("⚠️  No posts found")
            print("   This could mean:")
            print("   - Community has no recent posts")
            print("   - Community ID is incorrect")
            print("   - Need to adjust query")
            return
        
        print(f"✓ Found {len(posts_data)} posts")
        print("")
        
        # Store in database
        users_by_id = {user["id"]: user for user in users_data}
        session = get_session()
        posts_stored = 0
        
        try:
            for i, post_data in enumerate(posts_data, 1):
                author_id = post_data["author_id"]
                user_data = users_by_id.get(author_id)
                
                if not user_data:
                    continue
                
                # Create/update author
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
                else:
                    author.last_updated = datetime.utcnow()
                
                # Create post
                post = Post(
                    post_id=post_data["id"],
                    author_id=author_id,
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
                
                # Display post
                text_preview = post_data["text"][:80] + "..." if len(post_data["text"]) > 80 else post_data["text"]
                print(f"[{i}] @{user_data['username']}")
                print(f"    {text_preview}")
                print(f"    ❤️  {metrics.get('like_count', 0)} | 🔁 {metrics.get('retweet_count', 0)} | 💬 {metrics.get('reply_count', 0)}")
                print("")
            
            session.commit()
            
            print(f"✅ Stored {posts_stored} posts in database")
            print("")
            
            # Log collection
            log_collection(posts_stored)
            
            print("📊 Next steps:")
            print("   1. python analyze_posts.py  # Analyze sentiment")
            print("   2. python run_aggregator.py  # Create daily aggregate")
            print("")
            
            # Show quota usage
            show_quota_status()
            
        finally:
            session.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("")
        if "rate limit" in str(e).lower():
            print("⚠️  Rate limit hit. Wait 15-30 minutes and try again.")
            print("   Your quota is preserved - failed requests don't count.")


def log_collection(posts_count):
    """Log this collection to CSV"""
    log_file = "collection_log.csv"
    
    # Create file with headers if doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "day_of_week", "posts_collected", "cumulative_total"])
    
    # Read current total
    cumulative = posts_count
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                cumulative = int(rows[-1]["cumulative_total"]) + posts_count
    
    # Append new entry
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%A"),
            posts_count,
            cumulative
        ])


def show_quota_status():
    """Show current quota usage"""
    if not os.path.exists("collection_log.csv"):
        print("💰 Quota: 5 tweets used, ~95 remaining")
        return
    
    with open("collection_log.csv", "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if rows:
            total = int(rows[-1]["cumulative_total"])
            remaining = 100 - total
            print(f"💰 Quota: {total} tweets used, ~{remaining} remaining this month")


if __name__ == "__main__":
    asyncio.run(collect_community_posts())
