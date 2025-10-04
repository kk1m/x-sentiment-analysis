# Quickstart (Developer)

This quickstart validates the MVP flow end-to-end locally.

## 1) Prereqs
- Python 3.10+
- X API credentials (Free tier OK)
- Optional: OpenAI/Anthropic key for LLM

## 2) Create env
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install fastapi uvicorn[standard] pandas numpy pydantic sqlalchemy apscheduler httpx tweepy matplotlib plotly pytest pytest-mock
```

## 3) Configure secrets
Create `.env` in repo root:
```
X_API_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

## 4) Run daily batch (dry run)
```bash
bash scripts/run_daily_batch.sh --dry-run
```

## 5) Start API
```bash
uvicorn backend.src.main:app --reload
```

## 6) Validate
- GET `/health` → 200
- GET `/sentiment/trends?topic=Bitcoin&days=30` → JSON trend

## 7) Tests
```bash
pytest -q
```
