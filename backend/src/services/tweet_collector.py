"""Tweet Collector Service
Collects tweets from X API and stores them in database with quality filters
"""
import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from backend.src.services.x_api_client import XAPIClient
from backend.src.storage.database import get_session
from backend.src.models.author import Author
from backend.src.models.post import Post
from backend.src.models.engagement import Engagement


class TweetCollector:
    """
    Centralized service for collecting tweets from X API
    
    Features:
    - Quality filters (no retweets, English only, spam filtering)
    - Context-aware queries (ensures relevance to MSTR/crypto)
    - Batch size: 10 tweets (free tier compatible)
    """
    
    # Standard query with filters
    MSTR_QUERY = (
        "#MSTR "
        "(MicroStrategy OR Saylor OR Bitcoin OR BTC OR crypto OR price OR market OR stock OR shares OR treasury OR strategy OR bullish OR bearish OR buy OR sell OR hodl OR rally OR dump OR crash OR moon) "
        "-is:retweet -is:reply lang:en "
        "-giveaway -\"giving away\" -\"will receive\" -\"follow me\" -\"DM to own\""
    )
    
    def __init__(self, log_file: str = "data/logs/collection_log.csv"):
        self.x_client = XAPIClient()
        self.log_file = log_file
    
    def _log_collection(self, posts_count: int, status: str = "success", error_msg: Optional[str] = None):
        """Log collection attempt to CSV"""
        # Create file with headers if doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "date", "day_of_week", "status", "posts_collected", "error"])
        
        # Append this collection
        with open(self.log_file, "a", newline="") as f:
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
    
    async def collect_and_store_posts(
        self,
        since: Optional[datetime] = None,
        batch_job_id: Optional[str] = None,
        max_results: int = 10,
        query: Optional[str] = None,
        log: bool = True,
        verbose: bool = False
    ) -> int:
        """
        Collect tweets and store them in database
        
        Args:
            since: Collect posts after this datetime (optional)
            batch_job_id: Optional batch job ID for tracking
            max_results: Maximum number of tweets to collect (default 10, free tier limit)
            query: Custom query (uses MSTR_QUERY if not provided)
            log: Whether to log collection to CSV (default True)
            verbose: Whether to print verbose output (default False)
        
        Returns:
            Number of posts stored
        """
        # Use standard query if none provided
        if query is None:
            query = self.MSTR_QUERY
        
        session = None
        try:
            # Collect posts from X API
            response = await self.x_client.search_by_query(
                query=query,
                max_results=max_results,
                since=since
            )
            
            posts_data = response.get("data", [])
            users_data = response.get("includes", {}).get("users", [])
            
            if not posts_data:
                if log:
                    self._log_collection(0, status="success")
                return 0
            
            # Create user lookup
            users_by_id = {user["id"]: user for user in users_data}
            
            session = get_session()
            posts_stored = 0
            for post_data in posts_data:
                # Get or create author
                author_id = post_data["author_id"]
                user_data = users_by_id.get(author_id)
                
                if not user_data:
                    continue
                
                # Check if author exists
                author = session.query(Author).filter_by(user_id=author_id).first()
                
                if not author:
                    # Create new author
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
                    session.flush()  # Flush to get author ID without committing
                else:
                    # Update author metrics
                    author.followers_count = user_data["public_metrics"]["followers_count"]
                    author.following_count = user_data["public_metrics"]["following_count"]
                    author.last_updated = datetime.utcnow()
                
                # Check if post already exists (skip duplicates)
                existing_post = session.query(Post).filter_by(post_id=post_data["id"]).first()
                if existing_post:
                    continue
                
                # Create post
                post = Post(
                    post_id=post_data["id"],
                    author_id=author_id,
                    batch_job_id=batch_job_id,
                    text=post_data["text"],
                    language=post_data.get("lang"),
                    created_at=datetime.fromisoformat(post_data["created_at"].replace("Z", "+00:00")),
                    has_media=False,  # TODO: detect media
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
            
            # Log success
            if log:
                self._log_collection(posts_stored, status="success")
            
            if verbose:
                print(f"✅ Collected and stored {posts_stored} posts")
            
            return posts_stored
            
        except Exception as e:
            if session:
                session.rollback()
            
            # Log failure
            if log:
                error_type = "rate_limit" if "rate limit" in str(e).lower() else "error"
                self._log_collection(0, status=error_type, error_msg=str(e))
            
            if verbose:
                print(f"❌ Error: {e}")
                if "rate limit" in str(e).lower():
                    print("⚠️  Rate limit hit. Free tier allows:")
                    print("   - 500 tweets/month")
                    print("   - ~16 tweets/day")
                    print("   - Wait 15 minutes and try again")
            
            raise
        finally:
            if session:
                session.close()
