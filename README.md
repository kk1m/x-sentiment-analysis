# X Sentiment Analysis

A sophisticated sentiment analysis system for tracking bullish/bearish sentiment on Bitcoin, MSTR, and Bitcoin treasuries through X (Twitter) posts.

## Project Vision

Monitor daily sentiment trends on cryptocurrency topics by analyzing X posts with multi-dimensional weighting that accounts for post visibility, author influence, verification status, and bot detection. Designed for eventual public deployment as a portfolio credential.

## Key Features

- **Daily Batch Analysis**: End-of-day sentiment aggregation (not real-time)
- **Multi-Algorithm Comparison**: Compare LLM-based vs traditional ML sentiment models
- **Weighted Scoring**: High-visibility posts carry more weight than low-engagement posts
- **Bot Detection**: Filter out artificial engagement for signal quality
- **Historical Tracking**: Trend analysis over time with 1+ year data retention
- **Web-Ready Architecture**: API + frontend for public showcase

## Core Principles

1. **Signal Quality Over Noise** - Bot detection is non-negotiable
2. **Multi-Dimensional Weighted Analysis** - Visibility, influence, verification matter
3. **Algorithm Flexibility** - Support multiple sentiment models and compare results
4. **Batch Processing & Historical Tracking** - Daily aggregation with trend visibility
5. **Web-Ready Architecture** - Design for public deployment from day one
6. **Iterative Refinement** - Models and weights must be updatable

## Tech Stack

- **Language**: Python 3.10+
- **Storage**: SQLite (local) → PostgreSQL (production)
- **Data Processing**: pandas, numpy
- **Sentiment Analysis**: OpenAI/Anthropic API, Hugging Face transformers, VADER
- **X API**: tweepy/httpx (Free tier compatible)
- **Web Framework**: FastAPI
- **Visualization**: matplotlib/plotly, Streamlit/React
- **Testing**: pytest

## Getting Started

1. Review the constitution: `.specify/memory/constitution.md`
2. Use Windsurf slash commands to continue:
   - `/specify` - Create detailed technical specification
   - `/plan` - Generate implementation plan
   - `/tasks` - Break down into actionable tasks
   - `/implement` - Execute development

## Scope (v1.0)

**In Scope:**
- Bitcoin, MSTR, Bitcoin treasuries hashtag tracking
- Bullish/Bearish classification
- Multi-dimensional weighting (visibility, followers, verification, bot-likelihood)
- Historical trend tracking
- Multiple algorithm comparison
- Basic web API

**Out of Scope:**
- Real-time streaming
- Emotion detection beyond bullish/bearish
- Sarcasm detection
- Multi-language support
- Trading signals/recommendations

## API Constraints

- X API Free Tier: 500 tweets/month
- LLM API Budget: $50/month initial cap
- Must implement rate limiting and quota tracking

## Project Status

- ✅ Constitution defined (v1.0.0)
- ⏳ Specification pending
- ⏳ Implementation plan pending
- ⏳ Development pending

---

**Version**: 1.0.0 | **Created**: 2025-10-04
