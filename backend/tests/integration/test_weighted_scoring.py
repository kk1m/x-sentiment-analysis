"""
Integration Test: Weighted Scoring
Tests multi-dimensional weighting: visibility, influence, verification, bot penalty
This test WILL FAIL until T033 is implemented (TDD)
"""
import pytest
from unittest.mock import Mock


@pytest.fixture
def sample_posts_with_engagement():
    """Sample posts with varying engagement levels"""
    return [
        {
            "post_id": "1",
            "text": "Bitcoin bearish",
            "sentiment": "Bearish",
            "confidence": 0.9,
            "author": {
                "user_id": "user1",
                "followers_count": 100,
                "verified": False
            },
            "engagement": {
                "like_count": 1,
                "retweet_count": 0,
                "reply_count": 0,
                "quote_count": 0
            },
            "bot_score": 0.1
        },
        {
            "post_id": "2",
            "text": "Bitcoin bullish!",
            "sentiment": "Bullish",
            "confidence": 0.95,
            "author": {
                "user_id": "user2",
                "followers_count": 50000,
                "verified": True
            },
            "engagement": {
                "like_count": 100,
                "retweet_count": 50,
                "reply_count": 20,
                "quote_count": 10
            },
            "bot_score": 0.05
        }
    ]


def test_weighted_scoring_visibility_matters(sample_posts_with_engagement):
    """Posts with higher engagement should have more weight"""
    from backend.src.services.weighting_calculator import WeightingCalculator
    
    calculator = WeightingCalculator()
    
    # Post 1: 1 like, bearish
    weight1 = calculator.calculate_weight(sample_posts_with_engagement[0])
    
    # Post 2: 100 likes + 50 retweets, bullish
    weight2 = calculator.calculate_weight(sample_posts_with_engagement[1])
    
    # Post 2 should have significantly more weight
    assert weight2 > weight1
    assert weight2 / weight1 > 10  # At least 10x more weight


def test_weighted_scoring_influence_matters(sample_posts_with_engagement):
    """Authors with more followers should carry more weight"""
    from backend.src.services.weighting_calculator import WeightingCalculator
    
    calculator = WeightingCalculator()
    
    # Post 1: 100 followers
    weight1 = calculator.calculate_weight(sample_posts_with_engagement[0])
    
    # Post 2: 50,000 followers
    weight2 = calculator.calculate_weight(sample_posts_with_engagement[1])
    
    # Higher follower count should increase weight
    assert weight2 > weight1


def test_weighted_scoring_verification_multiplier():
    """Verified accounts should have higher weight multiplier"""
    from backend.src.services.weighting_calculator import WeightingCalculator
    
    calculator = WeightingCalculator()
    
    # Same engagement, different verification status
    unverified_post = {
        "author": {"followers_count": 10000, "verified": False},
        "engagement": {"like_count": 50, "retweet_count": 25, "reply_count": 10, "quote_count": 5},
        "bot_score": 0.1
    }
    
    verified_post = {
        "author": {"followers_count": 10000, "verified": True},
        "engagement": {"like_count": 50, "retweet_count": 25, "reply_count": 10, "quote_count": 5},
        "bot_score": 0.1
    }
    
    weight_unverified = calculator.calculate_weight(unverified_post)
    weight_verified = calculator.calculate_weight(verified_post)
    
    # Verified should have higher weight
    assert weight_verified > weight_unverified


def test_weighted_scoring_bot_penalty():
    """High bot-likelihood posts should have reduced weight"""
    from backend.src.services.weighting_calculator import WeightingCalculator
    
    calculator = WeightingCalculator()
    
    # Same post, different bot scores
    likely_human = {
        "author": {"followers_count": 10000, "verified": False},
        "engagement": {"like_count": 50, "retweet_count": 25, "reply_count": 10, "quote_count": 5},
        "bot_score": 0.1  # Low bot likelihood
    }
    
    likely_bot = {
        "author": {"followers_count": 10000, "verified": False},
        "engagement": {"like_count": 50, "retweet_count": 25, "reply_count": 10, "quote_count": 5},
        "bot_score": 0.9  # High bot likelihood
    }
    
    weight_human = calculator.calculate_weight(likely_human)
    weight_bot = calculator.calculate_weight(likely_bot)
    
    # Bot should have significantly reduced weight
    assert weight_bot < weight_human
    assert weight_bot / weight_human < 0.3  # At least 70% reduction


def test_weighted_scoring_formula_is_configurable():
    """Weighting formulas should be configurable and versioned"""
    from backend.src.services.weighting_calculator import WeightingCalculator
    from backend.src.models.weighting_config import WeightingConfig
    
    # Load default config
    calculator = WeightingCalculator()
    default_weight = calculator.calculate_weight({
        "author": {"followers_count": 1000, "verified": False},
        "engagement": {"like_count": 10, "retweet_count": 5, "reply_count": 2, "quote_count": 1},
        "bot_score": 0.2
    })
    
    # Load custom config
    custom_config = WeightingConfig(
        version="v2.0",
        visibility_formula="log(likes + retweets * 2)",
        influence_formula="sqrt(followers)",
        verification_multiplier=2.0,
        bot_penalty_formula="1 - bot_score"
    )
    
    calculator_custom = WeightingCalculator(config=custom_config)
    custom_weight = calculator_custom.calculate_weight({
        "author": {"followers_count": 1000, "verified": False},
        "engagement": {"like_count": 10, "retweet_count": 5, "reply_count": 2, "quote_count": 1},
        "bot_score": 0.2
    })
    
    # Different configs should produce different weights
    assert custom_weight != default_weight


def test_weighted_scoring_tracks_config_version():
    """Weighted scores should track which config version was used"""
    from backend.src.services.daily_aggregator import DailyAggregator
    from backend.src.storage.database import get_session
    from backend.src.models.daily_aggregate import DailyAggregate
    
    aggregator = DailyAggregator()
    
    # Run aggregation
    await aggregator.aggregate_daily_sentiment(
        date="2025-10-04",
        topic="Bitcoin"
    )
    
    # Check stored aggregate
    session = get_session()
    aggregate = session.query(DailyAggregate).filter_by(
        date="2025-10-04",
        topic="Bitcoin"
    ).first()
    
    assert aggregate.weighting_config_version is not None


def test_weighted_aggregate_calculation(sample_posts_with_engagement):
    """Daily aggregate should properly weight bullish vs bearish posts"""
    from backend.src.services.daily_aggregator import DailyAggregator
    
    aggregator = DailyAggregator()
    
    # Post 1: Bearish, low engagement (1 like)
    # Post 2: Bullish, high engagement (100 likes, 50 retweets)
    
    aggregate = aggregator.calculate_weighted_sentiment(sample_posts_with_engagement)
    
    # Despite having 1 bearish and 1 bullish post,
    # the aggregate should lean bullish due to higher weight
    assert aggregate["dominant_sentiment"] == "Bullish"
    assert aggregate["weighted_score"] > 0  # Positive = bullish


def test_weighted_scoring_handles_zero_engagement():
    """Weighting should handle posts with zero engagement gracefully"""
    from backend.src.services.weighting_calculator import WeightingCalculator
    
    calculator = WeightingCalculator()
    
    zero_engagement_post = {
        "author": {"followers_count": 100, "verified": False},
        "engagement": {"like_count": 0, "retweet_count": 0, "reply_count": 0, "quote_count": 0},
        "bot_score": 0.5
    }
    
    weight = calculator.calculate_weight(zero_engagement_post)
    
    # Should not crash, should return minimal weight
    assert weight >= 0
    assert weight < 1  # Very low weight for zero engagement


def test_weighted_scoring_normalizes_outliers():
    """Extreme engagement values should be normalized to prevent skew"""
    from backend.src.services.weighting_calculator import WeightingCalculator
    
    calculator = WeightingCalculator()
    
    # Viral post with extreme engagement
    viral_post = {
        "author": {"followers_count": 1000000, "verified": True},
        "engagement": {"like_count": 100000, "retweet_count": 50000, "reply_count": 10000, "quote_count": 5000},
        "bot_score": 0.1
    }
    
    # Normal post
    normal_post = {
        "author": {"followers_count": 1000, "verified": False},
        "engagement": {"like_count": 10, "retweet_count": 5, "reply_count": 2, "quote_count": 1},
        "bot_score": 0.2
    }
    
    weight_viral = calculator.calculate_weight(viral_post)
    weight_normal = calculator.calculate_weight(normal_post)
    
    # Viral should have more weight but not 10000x more (should be normalized)
    assert weight_viral > weight_normal
    assert weight_viral / weight_normal < 1000  # Reasonable ratio
