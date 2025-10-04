"""
Bulk Aggregator
Aggregates sentiment for all days with posts
"""
import asyncio
from datetime import date, timedelta
from sqlalchemy import func
from backend.src.services.daily_aggregator import DailyAggregator
from backend.src.storage.database import get_session
from backend.src.models.post import Post


async def main():
    print("🔄 Running bulk aggregator...")
    print("")
    
    session = get_session()
    
    # Find all unique dates with posts
    dates_with_posts = session.query(
        func.date(Post.created_at).label('date')
    ).distinct().all()
    
    session.close()
    
    if not dates_with_posts:
        print("⚠️  No posts found in database")
        return
    
    # Convert to date objects if they're strings
    dates = []
    for row in dates_with_posts:
        if isinstance(row.date, str):
            from datetime import datetime
            dates.append(datetime.strptime(row.date, "%Y-%m-%d").date())
        else:
            dates.append(row.date)
    dates.sort()
    
    print(f"📅 Found posts on {len(dates)} different days")
    print(f"   Range: {dates[0]} to {dates[-1]}")
    print("")
    
    aggregator = DailyAggregator()
    success_count = 0
    
    for i, target_date in enumerate(dates, 1):
        try:
            aggregate = await aggregator.aggregate_daily_sentiment(
                target_date=target_date,
                topic="Bitcoin",
                algorithm="openai-gpt4"
            )
            
            if aggregate:
                success_count += 1
                sentiment_emoji = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "🟡"}
                emoji = sentiment_emoji.get(aggregate.dominant_sentiment.value, "⚪")
                print(f"[{i}/{len(dates)}] {target_date}: {emoji} {aggregate.dominant_sentiment.value} (score: {aggregate.weighted_score:.3f}, posts: {aggregate.total_posts})")
        
        except Exception as e:
            print(f"[{i}/{len(dates)}] {target_date}: ❌ Error - {e}")
    
    print("")
    print(f"✅ Aggregated {success_count}/{len(dates)} days successfully!")
    print("")
    print("📊 Now view the dashboard:")
    print("   streamlit run dashboard.py")


if __name__ == "__main__":
    asyncio.run(main())
