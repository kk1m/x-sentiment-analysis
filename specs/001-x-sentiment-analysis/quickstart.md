# Quickstart (Developer)

This quickstart validates the MVP flow end-to-end locally.

## 1) Prereqs
- Python 3.10+
- X API credentials (Free tier OK)
- Optional: OpenAI/Anthropic key for LLM

### 1. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file:
```
X_API_KEY=your_twitter_bearer_token
OPENAI_API_KEY=optional  # Currently using keyword-based sentiment
```

### 3. Initialize Database
```bash
python -m backend.src.storage.init_db init
```

### 4. Collect Community Posts (Mon/Wed/Fri/Sun)
```bash
python collect_community_posts.py  # Collects 5 posts from MSTR community
python analyze_posts.py            # Analyzes sentiment + bot detection
python run_aggregator.py           # Creates daily aggregate
```

### 5. View Results
```bash
python -m uvicorn backend.src.main:app --reload
# Visit http://localhost:8000/docs
curl "http://localhost:8000/sentiment/trends?topic=MSTR&days=7"
```

## Full Documentation

See `QUICKSTART.md` in project root for complete workflow and troubleshooting.
