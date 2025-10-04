# Research: X Sentiment Analysis System

Date: 2025-10-04
Branch: 001-x-sentiment-analysis
Spec: /specs/001-x-sentiment-analysis/spec.md

## Decisions

- Data collection cadence: Daily batch at 23:59 local (configurable)
- Hashtag scope (v1.0): #Bitcoin, #MSTR, #BitcoinTreasuries
- Language scope: English only (exclude others)
- Sentiment classes: Bullish, Bearish, Neutral
- Algorithm strategy: Primary LLM API; fallback to local (FinBERT/VADER)
- Weighting: Visibility (likes/retweets), Influence (followers), Verification multiplier, Bot penalty
- Storage: SQLite dev; schema designed to upgrade to PostgreSQL
- API: FastAPI, REST endpoints for trends and aggregates
- Scheduling: APScheduler (dev), cron compatible

## Rationale

- Daily batch reduces complexity vs real-time but preserves trend utility
- Multi-algorithm allows validation and comparison; LLMs handle crypto slang well
- Weighting accounts for unequal post impact; avoids small noisy posts dominating
- SQLite keeps iteration fast; clean ORM model eases migration

## Alternatives Considered

- Real-time streaming (KafKa/Firehose): deferred due to scope and complexity
- Single-algorithm approach: rejected, reduces robustness/validation ability
- No bot detection in v1.0: rejected as it undermines signal quality principle

## Unknowns / Clarifications (Resolved)

- Bookmark/impression counts availability: may require paid X tier → mark optional/nullable
- X API quota: Free tier ~500 tweets/month; initial MVP acceptable; plan for paid tier later
- Confidence calibration across algorithms: will standardize to 0-1 scale

## Best Practices Notes

- Normalize engagement metrics before weighting to control outliers
- Keep weighting formula versioned and data lineage recorded
- Build small labeled dataset (100+ posts) for accuracy validation
- Add retries/backoff on external API calls; log structured errors
