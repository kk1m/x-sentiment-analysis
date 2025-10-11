"""
Post Collector Service
Collects posts from X API and stores them in database
"""
from datetime import datetime, timedelta
from typing import List, Dict
from backend.src.services.x_api_client import XAPIClient
from backend.src.storage.database import get_session
from backend.src.models.author import Author
from backend.src.models.post import Post
from backend.src.models.engagement import Engagement


class PostCollector:
    """Collects and stores posts from X API"""
    
    def __init__(self):
        self.x_client = XAPIClient()
    
    async def collect_daily_posts(
        self,
        hashtags: List[str],
        since: datetime
    ) -> List[Dict]:
        """
        Collect posts matching hashtags since given datetime
        
        Args:
            hashtags: List of hashtags to search
            since: Collect posts after this datetime
        
        Returns:
            List of post dictionaries
        """
        response = await self.x_client.search_by_hashtags(
            hashtags=hashtags,
            max_results=100,
            since=since
        )
        
        posts = response.get("data", [])
        return posts
    
    async def collect_and_store_daily_posts(
        self,
        hashtags: List[str],
        since: datetime,
        batch_job_id: str = None,
        max_results: int = 10
    ) -> int:
        """
        Collect posts and store them in database
        
        Args:
            hashtags: List of hashtags to search
            since: Collect posts after this datetime
            batch_job_id: Optional batch job ID for tracking
            max_results: Maximum number of tweets to collect (default 10)
        
        Returns:
            Number of posts stored
        """
        # Collect posts from X API
        response = await self.x_client.search_by_hashtags(
            hashtags=hashtags,
            max_results=max_results,
            since=since
        )
        
        posts_data = response.get("data", [])
        users_data = response.get("includes", {}).get("users", [])
        
        if not posts_data:
            return 0
        
        # Create user lookup
        users_by_id = {user["id"]: user for user in users_data}
        
        session = get_session()
        posts_stored = 0
        
        try:
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
            return posts_stored
            
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
