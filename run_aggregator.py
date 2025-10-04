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
    
    # Aggregate today's data
    today = date.today()
    
    aggregate = await aggregator.aggregate_daily_sentiment(
        target_date=today,
        topic="Bitcoin",
        algorithm="openai-gpt4"
    )
    
    if aggregate:
        print(f"\n✅ Daily aggregate created for {today}")
        print(f"   Topic: {aggregate.topic.value}")
        print(f"   Total posts: {aggregate.total_posts}")
        print(f"   Bullish: {aggregate.bullish_count} ({aggregate.bullish_percentage:.1f}%)")
        print(f"   Bearish: {aggregate.bearish_count} ({aggregate.bearish_percentage:.1f}%)")
        print(f"   Neutral: {aggregate.neutral_count} ({aggregate.neutral_percentage:.1f}%)")
        print(f"   Weighted score: {aggregate.weighted_score:.3f}")
        print(f"   Dominant sentiment: {aggregate.dominant_sentiment.value}")
        print(f"\n📊 Now try: curl \"http://localhost:8000/sentiment/trends?topic=Bitcoin&days=1\"")
    else:
        print(f"\n⚠️  No posts found for {today}")
        print("   Run demo.py first to create sample data")


if __name__ == "__main__":
    asyncio.run(main())
