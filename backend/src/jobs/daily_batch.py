"""
Daily Batch Job
Orchestrates daily data collection from X API
"""
import uuid
from datetime import datetime, timedelta
from backend.src.services.post_collector import PostCollector
from backend.src.storage.database import get_session
from backend.src.models.batch_job import BatchJob, JobStatus


async def run_daily_batch(
    hashtags: List[str] = None,
    lookback_hours: int = 24
) -> str:
    """
    Run daily batch collection job
    
    Args:
        hashtags: List of hashtags to search (default: Bitcoin, MSTR, BitcoinTreasuries)
        lookback_hours: How many hours back to collect (default: 24)
    
    Returns:
        Batch job ID
    """
    if hashtags is None:
        hashtags = ["#Bitcoin", "#MSTR", "#BitcoinTreasuries"]
    
    # Create batch job record
    batch_job_id = str(uuid.uuid4())
    session = get_session()
    
    batch_job = BatchJob(
        batch_job_id=batch_job_id,
        started_at=datetime.utcnow(),
        status=JobStatus.RUNNING,
        search_queries=str(hashtags)
    )
    session.add(batch_job)
    session.commit()
    session.close()
    
    try:
        # Collect posts
        collector = PostCollector()
        since = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        posts_stored = await collector.collect_and_store_daily_posts(
            hashtags=hashtags,
            since=since,
            batch_job_id=batch_job_id
        )
        
        # Update batch job - success
        session = get_session()
        batch_job = session.query(BatchJob).filter_by(batch_job_id=batch_job_id).first()
        batch_job.finished_at = datetime.utcnow()
        batch_job.status = JobStatus.COMPLETED
        batch_job.posts_collected = posts_stored
        batch_job.posts_stored = posts_stored
        session.commit()
        session.close()
        
        return batch_job_id
        
    except Exception as e:
        # Update batch job - failed
        session = get_session()
        batch_job = session.query(BatchJob).filter_by(batch_job_id=batch_job_id).first()
        batch_job.finished_at = datetime.utcnow()
        batch_job.status = JobStatus.FAILED
        batch_job.errors = str(e)
        batch_job.errors_count = 1
        session.commit()
        session.close()
        
        raise


# Import for type hints
from typing import List
