"""
Run Daily Aggregator
Aggregates sentiment data for today
"""
import asyncio
from datetime import date
from backend.src.services.daily_aggregator import DailyAggregator


async def main():
    print("🔄 Running daily aggregator...")
    
    aggregator = DailyAggregator()
    
    # Aggregate yesterday's data (or specify date)
    import sys
    if len(sys.argv) > 1:
        from datetime import datetime
        target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        # Default to yesterday since posts are usually from previous day
        from datetime import timedelta
        target_date = date.today() - timedelta(days=1)
    
    aggregate = await aggregator.aggregate_daily_sentiment(
        target_date=target_date,
        topic="Bitcoin",
        algorithm="openai-gpt4"
    )
    
    if aggregate:
        print(f"\n✅ Daily aggregate created for {target_date}")
        print(f"   Topic: {aggregate.topic.value}")
        print(f"   Total posts: {aggregate.total_posts}")
        print(f"   Bullish: {aggregate.bullish_count} ({aggregate.bullish_percentage:.1f}%)")
        print(f"   Bearish: {aggregate.bearish_count} ({aggregate.bearish_percentage:.1f}%)")
        print(f"   Neutral: {aggregate.neutral_count} ({aggregate.neutral_percentage:.1f}%)")
        print(f"   Weighted score: {aggregate.weighted_score:.3f}")
        print(f"   Dominant sentiment: {aggregate.dominant_sentiment.value}")
        print(f"\n📊 Now try: curl \"http://localhost:8000/sentiment/trends?topic=Bitcoin&days=1\"")
    else:
        print(f"\n⚠️  No posts found for {target_date}")
        print("   Run demo.py first to create sample data")


if __name__ == "__main__":
    asyncio.run(main())
