"""
Integration Test: Daily Batch Collection
Tests the end-to-end flow of collecting posts from X API
This test WILL FAIL until T024-T026 are implemented (TDD)
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


@pytest.fixture
def mock_x_api_response():
    """Mock X API response with sample posts"""
    return {
        "data": [
            {
                "id": "1234567890",
                "text": "Bitcoin to the moon! 🚀",
                "created_at": "2025-10-04T12:00:00.000Z",
                "author_id": "user123",
                "public_metrics": {
                    "like_count": 100,
                    "retweet_count": 50,
                    "reply_count": 10,
                    "quote_count": 5
                }
            },
            {
                "id": "0987654321",
                "text": "MSTR buying more Bitcoin!",
                "created_at": "2025-10-04T13:00:00.000Z",
                "author_id": "user456",
                "public_metrics": {
                    "like_count": 200,
                    "retweet_count": 75,
                    "reply_count": 20,
                    "quote_count": 10
                }
            }
        ],
        "includes": {
            "users": [
                {
                    "id": "user123",
                    "username": "crypto_bull",
                    "name": "Crypto Bull",
                    "verified": True,
                    "public_metrics": {
                        "followers_count": 10000,
                        "following_count": 500
                    }
                },
                {
                    "id": "user456",
                    "username": "bitcoin_hodler",
                    "name": "Bitcoin Hodler",
                    "verified": False,
                    "public_metrics": {
                        "followers_count": 5000,
                        "following_count": 300
                    }
                }
            ]
        }
    }


@pytest.mark.asyncio
async def test_daily_batch_collects_posts_from_x_api(mock_x_api_response):
    """Daily batch should collect posts matching hashtags"""
    # This will fail until we implement the post collector service
    from backend.src.services.post_collector import PostCollector
    from backend.src.services.x_api_client import XAPIClient
    
    with patch.object(XAPIClient, 'search_recent', return_value=mock_x_api_response):
        collector = PostCollector()
        posts = await collector.collect_daily_posts(
            hashtags=["#Bitcoin", "#MSTR", "#BitcoinTreasuries"],
            since=datetime.now() - timedelta(days=1)
        )
        
        assert len(posts) == 2
        assert posts[0]["text"] == "Bitcoin to the moon! 🚀"
        assert posts[1]["text"] == "MSTR buying more Bitcoin!"


@pytest.mark.asyncio
async def test_daily_batch_stores_post_metadata(mock_x_api_response):
    """Daily batch should store complete post metadata"""
    from backend.src.services.post_collector import PostCollector
    from backend.src.storage.database import get_session
    from backend.src.models.post import Post
    
    with patch('backend.src.services.x_api_client.XAPIClient.search_recent', 
               return_value=mock_x_api_response):
        collector = PostCollector()
        await collector.collect_and_store_daily_posts(
            hashtags=["#Bitcoin"],
            since=datetime.now() - timedelta(days=1)
        )
        
        # Verify posts were stored in database
        session = get_session()
        posts = session.query(Post).all()
        
        assert len(posts) >= 2
        assert posts[0].post_id is not None
        assert posts[0].text is not None
        assert posts[0].author_id is not None


@pytest.mark.asyncio
async def test_daily_batch_handles_rate_limiting():
    """Daily batch should pause and resume when X API rate limit is hit"""
    from backend.src.services.post_collector import PostCollector
    from backend.src.services.x_api_client import RateLimitError
    
    with patch('backend.src.services.x_api_client.XAPIClient.search_recent',
               side_effect=RateLimitError("Rate limit exceeded")):
        collector = PostCollector()
        
        # Should not crash, should log error and handle gracefully
        with pytest.raises(RateLimitError):
            await collector.collect_daily_posts(
                hashtags=["#Bitcoin"],
                since=datetime.now() - timedelta(days=1)
            )


@pytest.mark.asyncio
async def test_daily_batch_tracks_job_execution():
    """Daily batch should create BatchJob record with execution metadata"""
    from backend.src.jobs.daily_batch import run_daily_batch
    from backend.src.storage.database import get_session
    from backend.src.models.batch_job import BatchJob
    
    with patch('backend.src.services.x_api_client.XAPIClient.search_recent',
               return_value={"data": [], "includes": {}}):
        await run_daily_batch()
        
        # Verify batch job was recorded
        session = get_session()
        jobs = session.query(BatchJob).all()
        
        assert len(jobs) >= 1
        latest_job = jobs[-1]
        assert latest_job.status in ["completed", "failed"]
        assert latest_job.started_at is not None
        assert latest_job.finished_at is not None


@pytest.mark.asyncio
async def test_daily_batch_handles_empty_results():
    """Daily batch should handle days with no matching posts"""
    from backend.src.services.post_collector import PostCollector
    
    with patch('backend.src.services.x_api_client.XAPIClient.search_recent',
               return_value={"data": [], "includes": {}}):
        collector = PostCollector()
        posts = await collector.collect_daily_posts(
            hashtags=["#Bitcoin"],
            since=datetime.now() - timedelta(days=1)
        )
        
        assert posts == []
        # Should not crash, should log zero-post day
