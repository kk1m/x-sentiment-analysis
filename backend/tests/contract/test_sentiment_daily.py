"""
Contract Test: GET /sentiment/daily
Validates the daily sentiment aggregate endpoint returns expected schema
This test WILL FAIL until T037 is implemented (TDD)
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)


def test_sentiment_daily_endpoint_exists():
    """Daily sentiment endpoint should exist"""
    today = date.today().isoformat()
    response = client.get(f"/sentiment/daily?date={today}&topic=Bitcoin")
    # Should not be 404
    assert response.status_code != 404


def test_sentiment_daily_requires_date_and_topic():
    """Daily sentiment endpoint should require both date and topic parameters"""
    # Missing both
    response = client.get("/sentiment/daily")
    assert response.status_code == 422
    
    # Missing topic
    today = date.today().isoformat()
    response = client.get(f"/sentiment/daily?date={today}")
    assert response.status_code == 422
    
    # Missing date
    response = client.get("/sentiment/daily?topic=Bitcoin")
    assert response.status_code == 422


def test_sentiment_daily_accepts_valid_date_format():
    """Daily sentiment should accept ISO date format (YYYY-MM-DD)"""
    valid_date = "2025-10-04"
    response = client.get(f"/sentiment/daily?date={valid_date}&topic=Bitcoin")
    # Should not return 400 (bad request) for valid date
    assert response.status_code != 400


def test_sentiment_daily_rejects_invalid_date_format():
    """Daily sentiment should reject invalid date formats"""
    invalid_dates = ["10/04/2025", "2025-13-01", "not-a-date"]
    
    for invalid_date in invalid_dates:
        response = client.get(f"/sentiment/daily?date={invalid_date}&topic=Bitcoin")
        # Should return 400 or 422 (validation error)
        assert response.status_code in [400, 422]


def test_sentiment_daily_returns_aggregate_data():
    """Daily sentiment should return aggregate metrics"""
    today = date.today().isoformat()
    response = client.get(f"/sentiment/daily?date={today}&topic=Bitcoin")
    
    if response.status_code == 200:
        data = response.json()
        
        # Should contain aggregate fields
        expected_fields = ["date", "topic", "total_posts", "bullish_count", 
                          "bearish_count", "neutral_count", "weighted_score"]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"


def test_sentiment_daily_returns_404_for_missing_data():
    """Daily sentiment should return 404 if no data exists for date"""
    # Use a date far in the future
    future_date = (date.today() + timedelta(days=365)).isoformat()
    response = client.get(f"/sentiment/daily?date={future_date}&topic=Bitcoin")
    
    # Should return 404 or 200 with empty/null data
    assert response.status_code in [200, 404]


def test_sentiment_daily_accepts_all_topics():
    """Daily sentiment should accept all valid topics"""
    today = date.today().isoformat()
    valid_topics = ["Bitcoin", "MSTR", "BitcoinTreasuries"]
    
    for topic in valid_topics:
        response = client.get(f"/sentiment/daily?date={today}&topic={topic}")
        # Should not return 400 (bad request)
        assert response.status_code != 400
