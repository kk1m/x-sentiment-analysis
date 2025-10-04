"""
Sentiment API Endpoints
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional
from backend.src.storage.database import get_db
from backend.src.models.daily_aggregate import DailyAggregate, Topic

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


@router.get("/trends")
async def get_sentiment_trends(
    topic: str = Query(..., description="Topic: Bitcoin, MSTR, or BitcoinTreasuries"),
    days: int = Query(30, ge=1, le=365, description="Number of days to query"),
    algorithm: Optional[str] = Query(None, description="Filter by algorithm"),
    db: Session = Depends(get_db)
):
    """
    Get sentiment trends over time
    
    Returns daily sentiment data for the specified topic
    """
    # Validate topic
    valid_topics = ["Bitcoin", "MSTR", "BitcoinTreasuries"]
    if topic not in valid_topics:
        raise HTTPException(status_code=400, detail=f"Invalid topic. Must be one of: {valid_topics}")
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Query aggregates
    query = db.query(DailyAggregate).filter(
        DailyAggregate.topic == Topic[topic.upper().replace("TREASURIES", "_TREASURIES")],
        DailyAggregate.date >= start_date,
        DailyAggregate.date <= end_date
    )
    
    if algorithm:
        query = query.filter(DailyAggregate.algorithm_id == algorithm)
    
    aggregates = query.order_by(DailyAggregate.date).all()
    
    # Format response
    trends = []
    for agg in aggregates:
        trends.append({
            "date": agg.date.isoformat(),
            "topic": agg.topic.value,
            "algorithm_id": agg.algorithm_id,
            "total_posts": agg.total_posts,
            "bullish_count": agg.bullish_count,
            "bearish_count": agg.bearish_count,
            "neutral_count": agg.neutral_count,
            "bullish_percentage": agg.bullish_percentage,
            "bearish_percentage": agg.bearish_percentage,
            "neutral_percentage": agg.neutral_percentage,
            "weighted_score": agg.weighted_score,
            "dominant_sentiment": agg.dominant_sentiment.value
        })
    
    return trends


@router.get("/daily")
async def get_daily_sentiment(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    topic: str = Query(..., description="Topic: Bitcoin, MSTR, or BitcoinTreasuries"),
    db: Session = Depends(get_db)
):
    """
    Get sentiment aggregate for a specific day
    """
    # Validate topic
    valid_topics = ["Bitcoin", "MSTR", "BitcoinTreasuries"]
    if topic not in valid_topics:
        raise HTTPException(status_code=400, detail=f"Invalid topic. Must be one of: {valid_topics}")
    
    # Parse date
    try:
        query_date = date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Query aggregate
    aggregate = db.query(DailyAggregate).filter(
        DailyAggregate.date == query_date,
        DailyAggregate.topic == Topic[topic.upper().replace("TREASURIES", "_TREASURIES")]
    ).first()
    
    if not aggregate:
        raise HTTPException(status_code=404, detail="No data found for this date and topic")
    
    return {
        "date": aggregate.date.isoformat(),
        "topic": aggregate.topic.value,
        "algorithm_id": aggregate.algorithm_id,
        "total_posts": aggregate.total_posts,
        "bullish_count": aggregate.bullish_count,
        "bearish_count": aggregate.bearish_count,
        "neutral_count": aggregate.neutral_count,
        "bullish_percentage": aggregate.bullish_percentage,
        "bearish_percentage": aggregate.bearish_percentage,
        "neutral_percentage": aggregate.neutral_percentage,
        "weighted_score": aggregate.weighted_score,
        "dominant_sentiment": aggregate.dominant_sentiment.value,
        "total_likes": aggregate.total_likes,
        "total_retweets": aggregate.total_retweets,
        "avg_engagement_per_post": aggregate.avg_engagement_per_post
    }
