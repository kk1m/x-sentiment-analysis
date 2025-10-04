# Data Model (Conceptual)

Version: 0.1 (aligned with Constitution v1.1.0)

## Entities

### Author
- user_id (string, PK)
- username (string)
- display_name (string)
- followers_count (int)
- following_count (int)
- verified (bool)
- created_at (datetime)
- profile_description (text, optional)

### Post
- post_id (string, PK)
- author_id (FK → Author.user_id)
- text (text)
- created_at (datetime)
- language (string)
- has_media (bool)
- batch_job_id (FK → BatchJob.batch_job_id)

### Engagement
- post_id (FK → Post.post_id, PK)
- like_count (int)
- retweet_count (int)
- reply_count (int)
- quote_count (int)
- bookmark_count (int, nullable)
- impression_count (int, nullable)

### SentimentScore
- id (PK)
- post_id (FK → Post.post_id)
- algorithm_id (string)        # e.g., openai-gpt-4o, finbert
- algorithm_version (string)
- classification (enum: Bullish|Bearish|Neutral)
- confidence (float, 0..1)
- created_at (datetime)

### BotSignal
- id (PK)
- post_id (FK → Post.post_id)
- score (float, 0..1)
- inputs (json)                # optional indicators used
- created_at (datetime)

### WeightingConfig
- version (string, PK)
- visibility_formula (text)
- influence_formula (text)
- verification_multiplier (float)
- bot_penalty_formula (text)
- effective_date (date)

### DailyAggregate
- id (PK)
- date (date)
- topic (enum: Bitcoin|MSTR|BitcoinTreasuries)
- algorithm_id (string)
- total_posts (int)
- bullish_count (int)
- bearish_count (int)
- neutral_count (int)
- weighted_score (float)
- dominant_sentiment (enum)
- bot_detection_rate (float)

### BatchJob
- batch_job_id (string, PK)
- started_at (datetime)
- finished_at (datetime)
- status (enum: running|completed|failed)
- posts_collected (int)
- errors (text)

## Indexing
- Post.created_at, Post.author_id
- SentimentScore.post_id, algorithm_id
- DailyAggregate.date, topic, algorithm_id

## Notes
- Keep raw API payloads optionally in an archival table or blob store (deferred)
- All timestamps stored in UTC
