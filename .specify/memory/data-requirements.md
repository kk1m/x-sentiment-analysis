# Data Requirements Reference

This document clarifies the data capture requirements defined in Constitution Principle VII.

## Post Metadata to Capture

When processing each post from X API, the following metadata MUST be stored:

### Author Information
- User ID
- Username (@handle)
- Display name
- Follower count
- Following count
- Account creation date
- Verification status (blue checkmark)
- Profile description (for bot detection signals)

### Post Content
- Post ID (unique identifier)
- Post text/body
- Post creation timestamp
- Language (if available)
- Media attachments (count, types)
- URLs/links (if any)

### Engagement Metrics
- Like count
- Retweet count
- Reply count
- Quote tweet count
- Bookmark count (if available via API)
- Impression count (if available via API)
- View count (if available)

### Analysis Results
- Sentiment classification (Bullish/Bearish/Neutral)
- Sentiment score (confidence level)
- Algorithm used (e.g., "openai-gpt4", "finbert", "vader")
- Algorithm version
- Bot likelihood score (0-1)
- Weighted sentiment contribution
- Processing timestamp
- Batch job ID

### Data Lineage
- API call timestamp
- Batch job date
- Data collection method (hashtag search, user timeline, etc.)
- Search query/filter used
- API response metadata

## Daily Aggregate Metrics

For each day and each topic (Bitcoin, MSTR, Bitcoin treasuries), store:

### Volume Metrics
- Total posts collected
- Total posts after bot filtering
- Unique authors count
- Verified authors count

### Sentiment Distribution
- Bullish post count
- Bearish post count
- Neutral post count
- Bullish percentage
- Bearish percentage
- Neutral percentage

### Weighted Sentiment Scores
- Aggregate weighted sentiment score (per algorithm)
- Weighted bullish score
- Weighted bearish score
- Dominant sentiment (Bullish/Bearish/Neutral)

### Engagement Aggregates
- Total likes (sum)
- Total retweets (sum)
- Total replies (sum)
- Average engagement per post
- Median engagement per post
- Top 10 most engaged posts (IDs)

### Quality Metrics
- Bot detection rate (% flagged as bots)
- High-confidence sentiment % (e.g., >0.8 confidence)
- Low-confidence sentiment % (e.g., <0.5 confidence)
- Posts requiring manual review

## Database Schema Considerations

### Posts Table
- Primary key: post_id
- Indexes: timestamp, author_id, sentiment, bot_score
- Foreign key: batch_job_id

### Authors Table
- Primary key: user_id
- Indexes: follower_count, verification_status
- Deduplication: update on each batch if user data changed

### Daily Metrics Table
- Primary key: (date, topic, algorithm)
- Indexes: date, topic
- Enables trend queries and algorithm comparison

### Batch Jobs Table
- Primary key: batch_job_id
- Tracks: start_time, end_time, status, posts_collected, errors

## API Response Mapping

X API v2 fields to capture (Free Tier):
- `id` → post_id
- `text` → post_body
- `created_at` → post_timestamp
- `author_id` → user_id
- `public_metrics.like_count` → like_count
- `public_metrics.retweet_count` → retweet_count
- `public_metrics.reply_count` → reply_count
- `public_metrics.quote_count` → quote_count
- User expansion: `username`, `name`, `verified`, `public_metrics.followers_count`

**Note**: Bookmark count and impression count may require paid API tier. Mark as optional/nullable.

## Data Retention

- Raw posts: 1+ year minimum
- Daily aggregates: Indefinite (small storage footprint)
- Batch job logs: 90 days minimum
- Algorithm results: Store all versions for comparison

---

**Status**: Draft - to be refined during `/specify` phase
**Last Updated**: 2025-10-04
