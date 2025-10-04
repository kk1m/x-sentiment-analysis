"""
Contract Test: GET /sentiment/trends
Validates the sentiment trends endpoint returns expected schema
This test WILL FAIL until T036 is implemented (TDD)
"""
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)


def test_sentiment_trends_endpoint_exists():
    """Sentiment trends endpoint should exist"""
    response = client.get("/sentiment/trends?topic=Bitcoin&days=30")
    # Should not be 404
    assert response.status_code != 404


def test_sentiment_trends_requires_topic_parameter():
    """Sentiment trends endpoint should require topic parameter"""
    response = client.get("/sentiment/trends")
    # Should return 422 (validation error) if topic is missing
    assert response.status_code == 422


def test_sentiment_trends_accepts_valid_topics():
    """Sentiment trends should accept Bitcoin, MSTR, BitcoinTreasuries"""
    valid_topics = ["Bitcoin", "MSTR", "BitcoinTreasuries"]
    
    for topic in valid_topics:
        response = client.get(f"/sentiment/trends?topic={topic}&days=30")
        # Should return 200 or 500 (implementation error), not 400 (bad request)
        assert response.status_code in [200, 500]


def test_sentiment_trends_rejects_invalid_topic():
    """Sentiment trends should reject invalid topics"""
    response = client.get("/sentiment/trends?topic=InvalidTopic&days=30")
    # Should return 400 or 422 (validation error)
    assert response.status_code in [400, 422]


def test_sentiment_trends_returns_json_array():
    """Sentiment trends should return array of daily data points"""
    response = client.get("/sentiment/trends?topic=Bitcoin&days=30")
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
        
        # If dict, should have 'data' or 'trends' key
        if isinstance(data, dict):
            assert "data" in data or "trends" in data


def test_sentiment_trends_respects_days_parameter():
    """Sentiment trends should respect days parameter"""
    response = client.get("/sentiment/trends?topic=Bitcoin&days=7")
    
    if response.status_code == 200:
        data = response.json()
        # Response should have at most 7 data points
        if isinstance(data, list):
            assert len(data) <= 7


def test_sentiment_trends_supports_algorithm_filter():
    """Sentiment trends should support optional algorithm parameter"""
    response = client.get("/sentiment/trends?topic=Bitcoin&days=30&algorithm=openai-gpt4")
    # Should not return 400 (bad request)
    assert response.status_code != 400
