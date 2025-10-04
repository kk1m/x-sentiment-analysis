"""
Integration Test: Sentiment Classification
Tests bullish/bearish/neutral classification across multiple algorithms
This test WILL FAIL until T027-T031 are implemented (TDD)
"""
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def sample_posts():
    """Sample posts with clear sentiment"""
    return [
        {
            "post_id": "1",
            "text": "Bitcoin to the moon! 🚀 $100k incoming! BULLISH!",
            "expected_sentiment": "Bullish"
        },
        {
            "post_id": "2",
            "text": "Bitcoin crashing hard. Sell everything. This is the end.",
            "expected_sentiment": "Bearish"
        },
        {
            "post_id": "3",
            "text": "Bitcoin price is $45,000 today.",
            "expected_sentiment": "Neutral"
        },
        {
            "post_id": "4",
            "text": "MSTR continues to accumulate Bitcoin. Strong hands! 💎",
            "expected_sentiment": "Bullish"
        },
        {
            "post_id": "5",
            "text": "Bitcoin treasuries strategy looking risky in this market.",
            "expected_sentiment": "Bearish"
        }
    ]


@pytest.mark.asyncio
async def test_sentiment_classification_returns_bullish_bearish_neutral(sample_posts):
    """Sentiment classifier should return Bullish, Bearish, or Neutral"""
    from backend.src.services.sentiment_service import SentimentService
    
    service = SentimentService()
    
    for post in sample_posts:
        result = await service.classify_sentiment(
            text=post["text"],
            algorithm="openai-gpt4"
        )
        
        assert result["classification"] in ["Bullish", "Bearish", "Neutral"]
        assert 0 <= result["confidence"] <= 1


@pytest.mark.asyncio
async def test_sentiment_classification_high_confidence_for_clear_posts(sample_posts):
    """Classifier should have high confidence for clear sentiment"""
    from backend.src.services.sentiment_service import SentimentService
    
    service = SentimentService()
    
    # Test clearly bullish post
    bullish_post = sample_posts[0]  # "Bitcoin to the moon!"
    result = await service.classify_sentiment(
        text=bullish_post["text"],
        algorithm="openai-gpt4"
    )
    
    assert result["classification"] == "Bullish"
    assert result["confidence"] > 0.7  # High confidence threshold


@pytest.mark.asyncio
async def test_sentiment_classification_supports_multiple_algorithms(sample_posts):
    """Sentiment service should support multiple algorithms"""
    from backend.src.services.sentiment_service import SentimentService
    
    service = SentimentService()
    post_text = sample_posts[0]["text"]
    
    algorithms = ["openai-gpt4", "finbert", "vader"]
    
    for algorithm in algorithms:
        result = await service.classify_sentiment(
            text=post_text,
            algorithm=algorithm
        )
        
        assert result["algorithm_id"] == algorithm
        assert result["classification"] in ["Bullish", "Bearish", "Neutral"]


@pytest.mark.asyncio
async def test_sentiment_classification_stores_results_with_version():
    """Sentiment scores should be stored with algorithm version"""
    from backend.src.services.sentiment_service import SentimentService
    from backend.src.storage.database import get_session
    from backend.src.models.sentiment_score import SentimentScore
    from backend.src.models.post import Post
    
    # Create a test post
    session = get_session()
    test_post = Post(
        post_id="test123",
        text="Bitcoin looking strong!",
        author_id="user1",
        created_at="2025-10-04T12:00:00Z"
    )
    session.add(test_post)
    session.commit()
    
    # Classify and store
    service = SentimentService()
    await service.classify_and_store(
        post_id="test123",
        text="Bitcoin looking strong!",
        algorithm="openai-gpt4"
    )
    
    # Verify stored
    scores = session.query(SentimentScore).filter_by(post_id="test123").all()
    assert len(scores) >= 1
    assert scores[0].algorithm_id is not None
    assert scores[0].algorithm_version is not None
    assert scores[0].classification in ["Bullish", "Bearish", "Neutral"]


@pytest.mark.asyncio
async def test_sentiment_classification_handles_mixed_sentiment():
    """Classifier should handle posts with mixed sentiment"""
    from backend.src.services.sentiment_service import SentimentService
    
    service = SentimentService()
    
    # Mixed sentiment post
    mixed_text = "Bitcoin pumping but MSTR dumping. Not sure what to think."
    result = await service.classify_sentiment(
        text=mixed_text,
        algorithm="openai-gpt4"
    )
    
    # Should assign dominant sentiment
    assert result["classification"] in ["Bullish", "Bearish", "Neutral"]
    # Confidence should be lower for mixed sentiment
    assert result["confidence"] < 0.8


@pytest.mark.asyncio
async def test_sentiment_classification_fallback_on_api_failure():
    """Sentiment service should fallback to local model if LLM API fails"""
    from backend.src.services.sentiment_service import SentimentService
    
    service = SentimentService()
    
    # Mock OpenAI failure
    with patch('backend.src.services.sentiment.openai_analyzer.OpenAIAnalyzer.analyze',
               side_effect=Exception("API timeout")):
        
        result = await service.classify_sentiment(
            text="Bitcoin to the moon!",
            algorithm="openai-gpt4"
        )
        
        # Should have used fallback algorithm
        assert result["algorithm_id"] in ["finbert", "vader"]
        assert result["classification"] in ["Bullish", "Bearish", "Neutral"]


@pytest.mark.asyncio
async def test_sentiment_classification_excludes_non_english():
    """Classifier should exclude non-English posts (v1.0 constraint)"""
    from backend.src.services.sentiment_service import SentimentService
    
    service = SentimentService()
    
    # Non-English post
    result = await service.classify_sentiment(
        text="比特币涨到月球！",  # Chinese: "Bitcoin to the moon!"
        algorithm="openai-gpt4"
    )
    
    # Should return None or raise exception
    assert result is None or result["classification"] == "Unsupported"


@pytest.mark.asyncio
async def test_sentiment_classification_accuracy_validation():
    """Sentiment classifier should achieve >70% accuracy on labeled sample"""
    from backend.src.services.sentiment_service import SentimentService
    
    # This would use a manually labeled dataset (100+ posts)
    # For now, just test the validation function exists
    service = SentimentService()
    
    # Placeholder - actual validation would load labeled data
    accuracy = await service.validate_accuracy(
        algorithm="openai-gpt4",
        labeled_dataset_path="tests/fixtures/labeled_posts.json"
    )
    
    assert accuracy >= 0.70  # 70% minimum from NFR-006
