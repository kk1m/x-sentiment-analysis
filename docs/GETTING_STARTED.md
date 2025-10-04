# Getting Started with X Sentiment Analysis

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python -m backend.src.storage.init_db init
```

### 3. Create Demo Data

```bash
python demo.py
```

This creates:
- 2 sample authors
- 2 sample posts (1 bullish, 1 bearish)
- Sentiment scores
- Bot detection scores

### 4. Run Aggregation

```bash
python run_aggregator.py
```

This creates daily aggregate records from the demo posts.

### 5. Start the API Server

```bash
python -m uvicorn backend.src.main:app --reload
```

### 6. Test the API

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or use curl:
```bash
# Health check
curl http://localhost:8000/health

# Get sentiment trends
curl "http://localhost:8000/sentiment/trends?topic=Bitcoin&days=1"

# Get specific day
curl "http://localhost:8000/sentiment/daily?date=2025-10-04&topic=Bitcoin"
```

---

## Production Setup

### 1. Configure Environment Variables

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# X API Credentials (required for real data)
X_API_KEY=your_x_api_bearer_token_here

# LLM API Keys (optional, uses keyword matching if not provided)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./sentiment_analysis.db

# Batch Job Schedule (optional, defaults to 23:59)
BATCH_SCHEDULE_HOUR=23
BATCH_SCHEDULE_MINUTE=59
```

### 2. Get X API Credentials

1. Go to https://developer.twitter.com/
2. Create a new app
3. Generate Bearer Token
4. Add to `.env` as `X_API_KEY`

**Free Tier Limits:**
- 500 tweets/month
- ~16 tweets/day
- Sufficient for testing

**Paid Tier:**
- Basic: $100/month (10,000 tweets/month)
- Pro: $5,000/month (1M tweets/month)

### 3. Get LLM API Key (Optional)

**Option A: OpenAI**
1. Go to https://platform.openai.com/
2. Create API key
3. Add to `.env` as `OPENAI_API_KEY`
4. Cost: ~$0.01-0.03 per 1k tokens

**Option B: Anthropic Claude**
1. Go to https://console.anthropic.com/
2. Create API key
3. Add to `.env` as `ANTHROPIC_API_KEY`
4. Cost: Similar to OpenAI

**Note:** System works without LLM keys using keyword-based sentiment analysis.

### 4. Start the Full System

```bash
# Start API server + scheduler together
python start.py
```

This starts:
- **API Server** on port 8000
- **Job Scheduler** (daily batch at 23:59)

Or run separately:

```bash
# Terminal 1: API Server
python -m uvicorn backend.src.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Scheduler
python -m backend.src.jobs.scheduler
```

---

## Manual Operations

### Run Daily Batch Manually

```bash
./scripts/run_daily_batch.sh
```

Or with Python:

```python
import asyncio
from backend.src.jobs.daily_batch import run_daily_batch

async def main():
    batch_job_id = await run_daily_batch(
        hashtags=["#Bitcoin", "#MSTR", "#BitcoinTreasuries"],
        lookback_hours=24
    )
    print(f"Batch job: {batch_job_id}")

asyncio.run(main())
```

### Run Aggregation Manually

```bash
python run_aggregator.py
```

### Reset Database

```bash
python -m backend.src.storage.init_db reset
```

**Warning:** This deletes all data!

---

## Database Operations

### View Data

```bash
# Open SQLite CLI
sqlite3 sentiment_analysis.db

# View tables
.tables

# Query authors
SELECT user_id, username, followers_count, verified FROM authors;

# Query posts
SELECT post_id, substr(text, 1, 50) as text FROM posts;

# Query sentiment scores
SELECT post_id, classification, confidence FROM sentiment_scores;

# Query daily aggregates
SELECT date, topic, dominant_sentiment, weighted_score FROM daily_aggregates;

# Exit
.quit
```

### Migrate to PostgreSQL

1. Install PostgreSQL
2. Create database:
   ```sql
   CREATE DATABASE sentiment_analysis;
   ```

3. Update `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/sentiment_analysis
   ```

4. Initialize:
   ```bash
   python -m backend.src.storage.init_db init
   ```

---

## Testing

### Run All Tests

```bash
pytest backend/tests/ -v
```

### Run Specific Test Suite

```bash
# Contract tests (API endpoints)
pytest backend/tests/contract/ -v

# Integration tests (business logic)
pytest backend/tests/integration/ -v

# Specific test file
pytest backend/tests/contract/test_health.py -v
```

### Run Tests with Coverage

```bash
pytest backend/tests/ --cov=backend/src --cov-report=html
open htmlcov/index.html
```

---

## Monitoring

### Check Batch Job Status

```python
from backend.src.storage.database import get_session
from backend.src.models.batch_job import BatchJob

session = get_session()
jobs = session.query(BatchJob).order_by(BatchJob.started_at.desc()).limit(10).all()

for job in jobs:
    print(f"{job.started_at} - {job.status.value} - {job.posts_collected} posts")
```

### Check Daily Aggregates

```python
from backend.src.storage.database import get_session
from backend.src.models.daily_aggregate import DailyAggregate

session = get_session()
aggregates = session.query(DailyAggregate).order_by(DailyAggregate.date.desc()).limit(7).all()

for agg in aggregates:
    print(f"{agg.date} - {agg.topic.value} - {agg.dominant_sentiment.value} ({agg.weighted_score:.2f})")
```

---

## Troubleshooting

### "No module named 'backend'"

Make sure you're running from the project root:
```bash
cd /path/to/x_sentiment_analysis
python -m backend.src.main
```

### "X_API_KEY not found"

Add your X API bearer token to `.env`:
```env
X_API_KEY=your_token_here
```

### "Rate limit exceeded"

X API free tier is limited. Wait for quota reset or upgrade to paid tier.

### Database locked

Close any open SQLite connections:
```bash
# Find processes
lsof sentiment_analysis.db

# Kill if needed
kill <PID>
```

### Port 8000 already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill <PID>

# Or use different port
uvicorn backend.src.main:app --port 8001
```

---

## Next Steps

1. **Add Real X API Credentials** - Get actual tweet data
2. **Implement Real LLM Sentiment** - Replace keyword matching
3. **Deploy to Cloud** - Railway, Fly.io, or AWS
4. **Build Frontend** - React dashboard for visualization
5. **Add More Topics** - Expand beyond Bitcoin/MSTR
6. **Tune Weighting** - Optimize formulas based on results

---

## Resources

- **Constitution**: `.specify/memory/constitution.md` - Project principles
- **Weighting Explained**: `docs/WEIGHTING_EXPLAINED.md` - How sentiment weighting works
- **API Docs**: http://localhost:8000/docs (when server running)
- **Specification**: `specs/001-x-sentiment-analysis/spec.md` - Full requirements
- **Tasks**: `specs/001-x-sentiment-analysis/tasks.md` - Implementation checklist
