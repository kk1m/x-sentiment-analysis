# Sentiment Weighting System Explained

## Overview

Not all posts are equal. A tweet with 100,000 likes from a verified account with 1M followers should carry more weight than a tweet with 5 likes from a new account with 100 followers.

Our weighting system ensures that **high-visibility, high-influence posts have proportionally more impact on the daily sentiment score**, while preventing any single viral post from completely dominating the analysis.

## The Formula

### Final Weight = Visibility × Influence × Verification × Bot Penalty

Each post receives a weight calculated from four components:

---

## 1. Visibility Weight (Engagement Metrics)

**Formula:**
```
log(1 + likes + retweets×2 + replies + quotes)
```

**Why logarithmic?**
- Prevents viral posts from dominating unfairly
- A post with 10,000 likes is more influential than one with 100 likes, but not 100x more
- Diminishing returns at scale (realistic impact modeling)

**Why retweets count 2x?**
- Retweets amplify reach more than likes
- A retweet shows stronger conviction (sharing vs. just liking)

**Examples:**
| Engagement | Calculation | Weight |
|------------|-------------|--------|
| 10 likes, 5 retweets | log(1 + 10 + 10) = log(21) | 3.04 |
| 100 likes, 50 retweets | log(1 + 100 + 100) = log(201) | 5.30 |
| 1,000 likes, 500 retweets | log(1 + 1000 + 1000) = log(2001) | 7.60 |
| 10,000 likes, 5,000 retweets | log(1 + 10000 + 10000) = log(20001) | 9.90 |

**Key insight:** Going from 100 to 10,000 likes (100x increase) only increases weight by ~1.9x (5.30 → 9.90)

---

## 2. Influence Weight (Follower Count)

**Formula:**
```
log(1 + followers)
```

**Why logarithmic?**
- An account with 1M followers is more influential than one with 1k, but not 1000x more
- Prevents celebrity accounts from completely drowning out everyone else
- Reflects real-world influence dynamics (diminishing marginal impact)

**Examples:**
| Followers | Calculation | Weight |
|-----------|-------------|--------|
| 100 | log(101) | 4.62 |
| 1,000 | log(1,001) | 6.91 |
| 10,000 | log(10,001) | 9.21 |
| 100,000 | log(100,001) | 11.51 |
| 1,000,000 | log(1,000,001) | 13.82 |

**Key insight:** 1M followers is only ~3x more influential than 100 followers (13.82 vs 4.62), not 10,000x

---

## 3. Verification Multiplier

**Formula:**
```
1.5 if verified else 1.0
```

**Why 1.5x?**
- Verified accounts are less likely to be bots
- Verified accounts tend to have more credible opinions
- 50% boost is significant but not overwhelming

**Example:**
- Verified account with 10k followers: weight = 9.21 × **1.5** = **13.82**
- Unverified account with 10k followers: weight = 9.21 × **1.0** = **9.21**

---

## 4. Bot Penalty

**Formula:**
```
max(0, 1 - bot_score × 2)
```

**How it works:**
| Bot Score | Penalty | Effect |
|-----------|---------|--------|
| 0.0 (human) | 1.0 | No reduction |
| 0.2 (likely human) | 0.6 | 40% reduction |
| 0.4 (uncertain) | 0.2 | 80% reduction |
| 0.5+ (likely bot) | 0.0 | **Completely excluded** |

**Why aggressive penalty?**
- Bot-generated sentiment is noise, not signal
- False positives (marking humans as bots) are acceptable
- False negatives (missing bots) undermine the entire analysis
- Aligns with Constitution Principle I: "Signal Quality Over Noise"

---

## Complete Example

### Post 1: High-Engagement Bullish Tweet

**Content:** "Bitcoin to the moon! 🚀 $100k incoming!"

**Metrics:**
- 100 likes, 50 retweets, 20 replies, 10 quotes
- Author: 10,000 followers, verified
- Bot score: 0.0 (human)
- Sentiment: Bullish

**Weight Calculation:**
1. Visibility: log(1 + 100 + 100 + 20 + 10) = log(231) = **5.44**
2. Influence: log(1 + 10,000) = **9.21**
3. Verification: **1.5**
4. Bot penalty: **1.0**

**Final Weight: 5.44 × 9.21 × 1.5 × 1.0 = 75.2**

---

### Post 2: Low-Engagement Bearish Tweet

**Content:** "Bitcoin crash incoming. Sell everything."

**Metrics:**
- 10 likes, 5 retweets, 2 replies, 1 quote
- Author: 5,000 followers, not verified
- Bot score: 0.15 (likely human)
- Sentiment: Bearish

**Weight Calculation:**
1. Visibility: log(1 + 10 + 10 + 2 + 1) = log(24) = **3.18**
2. Influence: log(1 + 5,000) = **8.52**
3. Verification: **1.0**
4. Bot penalty: 1 - (0.15 × 2) = **0.70**

**Final Weight: 3.18 × 8.52 × 1.0 × 0.70 = 18.96**

---

## Aggregate Weighted Sentiment

**Formula:**
```
weighted_score = (bullish_weight - bearish_weight) / total_weight
```

**Using our example:**
```
weighted_score = (75.2 - 18.96) / (75.2 + 18.96)
               = 56.24 / 94.16
               = 0.597
```

**Interpretation:**
- Score range: -1.0 (completely bearish) to +1.0 (completely bullish)
- 0.597 = **Moderately Bullish**
- Even though we have 50% bullish and 50% bearish posts by count, the weighted sentiment is bullish because the bullish post had much higher engagement

---

## Dominant Sentiment Classification

**Thresholds:**
- `weighted_score > 0.1` → **Bullish**
- `weighted_score < -0.1` → **Bearish**
- `-0.1 ≤ weighted_score ≤ 0.1` → **Neutral**

**Why 0.1 threshold?**
- Provides a neutral zone for genuinely mixed sentiment
- Prevents flip-flopping between bullish/bearish on small changes
- Requires clear directional bias to declare dominant sentiment

---

## Why This Approach?

### Problem: Naive Counting Fails

If we just counted posts:
- 100 low-quality bot posts saying "bearish" would outweigh 1 high-quality human post with 10k likes
- One viral meme could skew the entire day's sentiment
- Bots could easily manipulate the signal

### Solution: Multi-Dimensional Weighting

Our approach:
- ✅ High-engagement posts carry more weight (visibility matters)
- ✅ Influential accounts carry more weight (credibility matters)
- ✅ Verified accounts get a boost (trust matters)
- ✅ Bot-likely posts are penalized or excluded (signal quality matters)
- ✅ Logarithmic scaling prevents outlier dominance (fairness matters)

---

## Configurable & Versioned

The weighting formulas are stored in the `weighting_configs` table and versioned:

```python
WeightingConfig(
    version="v1.0",
    visibility_formula="log(1 + likes + retweets * 2 + replies + quotes)",
    influence_formula="log(1 + followers)",
    verification_multiplier=1.5,
    bot_penalty_formula="max(0, 1 - bot_score * 2)"
)
```

**Benefits:**
- Can A/B test different formulas
- Can reprocess historical data with new weights
- Can track which version generated which results
- Can tune formulas based on validation results

---

## Future Enhancements

**Potential improvements:**
- Time decay (recent posts weighted higher)
- Reply depth weighting (viral threads vs single tweets)
- Author reputation score (historical accuracy)
- Topic-specific weighting (different formulas for different topics)
- Machine learning to optimize weights based on market correlation

---

## Validation

To validate the weighting system:

1. **Manual review**: Check top-weighted posts make sense
2. **Correlation analysis**: Compare weighted sentiment to price movements
3. **Bot detection accuracy**: Measure false positive/negative rates
4. **A/B testing**: Compare different formula versions
5. **Edge case testing**: Ensure viral posts don't dominate unfairly

---

## Summary

The weighting system transforms raw post counts into meaningful sentiment signals by:

1. **Logarithmic scaling** - Prevents outliers from dominating
2. **Multi-factor weighting** - Engagement + Influence + Verification + Bot detection
3. **Configurable formulas** - Can be tuned and improved over time
4. **Versioned tracking** - Know which weights generated which results

**Result:** A robust sentiment score that reflects genuine market sentiment, not just post volume or bot manipulation.
