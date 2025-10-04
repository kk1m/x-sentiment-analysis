"""
Job Scheduler
Schedules daily batch jobs using APScheduler
"""
import os
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.src.jobs.daily_batch import run_daily_batch
from backend.src.services.daily_aggregator import DailyAggregator
from datetime import date


async def daily_collection_job():
    """
    Daily job: Collect posts from X API
    Runs at configured time (default: 23:59)
    """
    print(f"[{datetime.now()}] Starting daily collection job...")
    
    try:
        batch_job_id = await run_daily_batch(
            hashtags=["#Bitcoin", "#MSTR", "#BitcoinTreasuries"],
            lookback_hours=24
        )
        print(f"[{datetime.now()}] ✓ Daily collection completed. Batch job: {batch_job_id}")
        
        # Run aggregation after collection
        await daily_aggregation_job()
        
    except Exception as e:
        print(f"[{datetime.now()}] ✗ Daily collection failed: {e}")


async def daily_aggregation_job():
    """
    Daily job: Aggregate sentiment data
    Runs after collection job
    """
    print(f"[{datetime.now()}] Starting daily aggregation job...")
    
    try:
        aggregator = DailyAggregator()
        today = date.today()
        
        # Aggregate for each topic
        topics = ["Bitcoin", "MSTR", "BitcoinTreasuries"]
        algorithms = ["openai-gpt4", "vader"]
        
        for topic in topics:
            for algorithm in algorithms:
                aggregate = await aggregator.aggregate_daily_sentiment(
                    target_date=today,
                    topic=topic,
                    algorithm=algorithm
                )
                
                if aggregate:
                    print(f"[{datetime.now()}] ✓ Aggregated {topic} ({algorithm}): {aggregate.dominant_sentiment.value}")
        
        print(f"[{datetime.now()}] ✓ Daily aggregation completed")
        
    except Exception as e:
        print(f"[{datetime.now()}] ✗ Daily aggregation failed: {e}")


def start_scheduler():
    """
    Start the job scheduler
    
    Schedules:
    - Daily collection at 23:59 (configurable via env)
    """
    scheduler = AsyncIOScheduler()
    
    # Get schedule from environment or use defaults
    hour = int(os.getenv("BATCH_SCHEDULE_HOUR", "23"))
    minute = int(os.getenv("BATCH_SCHEDULE_MINUTE", "59"))
    
    # Schedule daily collection job
    scheduler.add_job(
        daily_collection_job,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="daily_collection",
        name="Daily X Post Collection",
        replace_existing=True
    )
    
    print(f"📅 Scheduler started. Daily collection scheduled for {hour:02d}:{minute:02d}")
    print(f"   Next run: {scheduler.get_job('daily_collection').next_run_time}")
    
    scheduler.start()
    return scheduler


async def run_scheduler():
    """
    Run the scheduler (for standalone execution)
    """
    scheduler = start_scheduler()
    
    try:
        # Keep the scheduler running
        while True:
            await asyncio.sleep(60)  # Check every minute
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Shutting down scheduler...")
        scheduler.shutdown()


if __name__ == "__main__":
    print("🚀 Starting X Sentiment Analysis Scheduler...")
    asyncio.run(run_scheduler())
