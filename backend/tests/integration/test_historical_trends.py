"""
Integration Test: Historical Trend Queries
Tests querying sentiment trends over arbitrary date ranges
This test WILL FAIL until T034-T037 are implemented (TDD)
"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock


@pytest.fixture
def sample_daily_aggregates():
    """Sample daily aggregates for 30 days"""
    aggregates = []
    base_date = date.today() - timedelta(days=30)
    
    for i in range(30):
        current_date = base_date + timedelta(days=i)
        aggregates.append({
            "date": current_date.isoformat(),
            "topic": "Bitcoin",
            "algorithm_id": "openai-gpt4",
            "total_posts": 50 + (i * 2),
            "bullish_count": 30 + i,
            "bearish_count": 15,
            "neutral_count": 5,
            "weighted_score": 0.5 + (i * 0.01),  # Trending up
            "dominant_sentiment": "Bullish" if i > 15 else "Neutral"
        })
    
    return aggregates


@pytest.mark.asyncio
async def test_historical_trends_query_date_range(sample_daily_aggregates):
    """Should query trends over arbitrary date range"""
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    trends = await service.get_trends(
        topic="Bitcoin",
        start_date=start_date,
        end_date=end_date
    )
    
    assert len(trends) <= 30
    assert all(trend["topic"] == "Bitcoin" for trend in trends)


@pytest.mark.asyncio
async def test_historical_trends_filter_by_topic():
    """Should filter trends by topic (Bitcoin, MSTR, BitcoinTreasuries)"""
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    topics = ["Bitcoin", "MSTR", "BitcoinTreasuries"]
    
    for topic in topics:
        trends = await service.get_trends(
            topic=topic,
            days=30
        )
        
        assert all(trend["topic"] == topic for trend in trends)


@pytest.mark.asyncio
async def test_historical_trends_filter_by_algorithm():
    """Should filter trends by algorithm"""
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    algorithms = ["openai-gpt4", "finbert", "vader"]
    
    for algorithm in algorithms:
        trends = await service.get_trends(
            topic="Bitcoin",
            days=30,
            algorithm=algorithm
        )
        
        assert all(trend["algorithm_id"] == algorithm for trend in trends)


@pytest.mark.asyncio
async def test_historical_trends_compare_algorithms():
    """Should support comparing multiple algorithms side-by-side"""
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    comparison = await service.compare_algorithms(
        topic="Bitcoin",
        days=30,
        algorithms=["openai-gpt4", "finbert", "vader"]
    )
    
    # Should return data for all algorithms
    assert "openai-gpt4" in comparison
    assert "finbert" in comparison
    assert "vader" in comparison
    
    # Each algorithm should have trend data
    for algorithm, trends in comparison.items():
        assert len(trends) > 0


@pytest.mark.asyncio
async def test_historical_trends_returns_empty_for_missing_data():
    """Should return empty array if no data exists for date range"""
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    # Query far future dates
    future_start = (date.today() + timedelta(days=365)).isoformat()
    future_end = (date.today() + timedelta(days=395)).isoformat()
    
    trends = await service.get_trends(
        topic="Bitcoin",
        start_date=future_start,
        end_date=future_end
    )
    
    assert trends == []


@pytest.mark.asyncio
async def test_historical_trends_includes_all_metrics():
    """Trend data should include all daily aggregate metrics"""
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    trends = await service.get_trends(
        topic="Bitcoin",
        days=7
    )
    
    if len(trends) > 0:
        trend = trends[0]
        
        # Required fields
        required_fields = [
            "date", "topic", "total_posts", 
            "bullish_count", "bearish_count", "neutral_count",
            "weighted_score", "dominant_sentiment"
        ]
        
        for field in required_fields:
            assert field in trend


@pytest.mark.asyncio
async def test_historical_trends_ordered_by_date():
    """Trends should be returned in chronological order"""
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    trends = await service.get_trends(
        topic="Bitcoin",
        days=30
    )
    
    if len(trends) > 1:
        # Check dates are in ascending order
        dates = [trend["date"] for trend in trends]
        assert dates == sorted(dates)


@pytest.mark.asyncio
async def test_historical_trends_calculates_percentages():
    """Trends should include sentiment percentages"""
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    trends = await service.get_trends(
        topic="Bitcoin",
        days=7
    )
    
    if len(trends) > 0:
        trend = trends[0]
        
        # Should have percentage fields
        assert "bullish_percentage" in trend
        assert "bearish_percentage" in trend
        assert "neutral_percentage" in trend
        
        # Percentages should sum to ~100
        total_pct = (trend["bullish_percentage"] + 
                    trend["bearish_percentage"] + 
                    trend["neutral_percentage"])
        assert 99 <= total_pct <= 101  # Allow for rounding


@pytest.mark.asyncio
async def test_historical_trends_api_performance():
    """Trend queries should respond within 2 seconds (NFR-002)"""
    import time
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    start_time = time.time()
    
    trends = await service.get_trends(
        topic="Bitcoin",
        days=30
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Should complete within 2 seconds
    assert duration < 2.0


@pytest.mark.asyncio
async def test_historical_trends_supports_reprocessing():
    """Should support querying trends from reprocessed data"""
    from backend.src.services.trend_service import TrendService
    from backend.src.services.sentiment_service import SentimentService
    
    # Reprocess historical data with new algorithm
    sentiment_service = SentimentService()
    await sentiment_service.reprocess_historical_posts(
        start_date=(date.today() - timedelta(days=7)).isoformat(),
        end_date=date.today().isoformat(),
        algorithm="finbert-v2"
    )
    
    # Query trends with new algorithm
    trend_service = TrendService()
    trends = await trend_service.get_trends(
        topic="Bitcoin",
        days=7,
        algorithm="finbert-v2"
    )
    
    # Should have data from reprocessing
    assert len(trends) > 0


@pytest.mark.asyncio
async def test_historical_trends_visualization_data():
    """Should provide data formatted for visualization"""
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    viz_data = await service.get_visualization_data(
        topic="Bitcoin",
        days=30
    )
    
    # Should have separate arrays for plotting
    assert "dates" in viz_data
    assert "weighted_scores" in viz_data
    assert "bullish_counts" in viz_data
    assert "bearish_counts" in viz_data
    
    # Arrays should be same length
    assert len(viz_data["dates"]) == len(viz_data["weighted_scores"])


@pytest.mark.asyncio
async def test_historical_trends_handles_gaps_in_data():
    """Should handle days with missing data gracefully"""
    from backend.src.services.trend_service import TrendService
    
    service = TrendService()
    
    # Query range that may have gaps
    trends = await service.get_trends(
        topic="Bitcoin",
        days=90
    )
    
    # Should not crash, should return available data
    assert isinstance(trends, list)
    
    # Gaps should be represented (null or interpolated)
    # Implementation can choose strategy


@pytest.mark.asyncio
async def test_historical_trends_aggregates_multiple_batches():
    """Should aggregate data from multiple daily batch runs"""
    from backend.src.services.trend_service import TrendService
    from backend.src.storage.database import get_session
    from backend.src.models.daily_aggregate import DailyAggregate
    
    # Simulate multiple aggregates for same day (different algorithms)
    session = get_session()
    today = date.today().isoformat()
    
    # Should combine/separate based on algorithm filter
    trends_all = await service.get_trends(topic="Bitcoin", days=1)
    trends_openai = await service.get_trends(topic="Bitcoin", days=1, algorithm="openai-gpt4")
    
    # All algorithms vs single algorithm
    assert len(trends_all) >= len(trends_openai)
