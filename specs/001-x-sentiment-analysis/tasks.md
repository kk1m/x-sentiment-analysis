# Tasks: X Sentiment Analysis System

**Input**: Design documents from `/specs/001-x-sentiment-analysis/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 3.1: Setup

- [ ] **T001** Create project directory structure: `backend/src/{api,jobs,models,services,storage}`, `backend/tests/{contract,integration,unit}`, `scripts/`
- [ ] **T002** Initialize Python project with `requirements.txt`: FastAPI, uvicorn, pandas, numpy, pydantic, sqlalchemy, apscheduler, httpx, tweepy, matplotlib, plotly, pytest, pytest-mock, python-dotenv
- [ ] **T003** [P] Configure `.env.example` template for X_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY
- [ ] **T004** [P] Set up `.gitignore` for Python (venv, .env, __pycache__, *.db)
- [ ] **T005** [P] Create `backend/src/main.py` FastAPI app skeleton with health endpoint

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests
- [ ] **T006** [P] Contract test GET /health in `backend/tests/contract/test_health.py`
- [ ] **T007** [P] Contract test GET /sentiment/trends in `backend/tests/contract/test_sentiment_trends.py`
- [ ] **T008** [P] Contract test GET /sentiment/daily in `backend/tests/contract/test_sentiment_daily.py`

### Integration Tests
- [ ] **T009** [P] Integration test: daily batch collects posts in `backend/tests/integration/test_daily_batch.py`
- [ ] **T010** [P] Integration test: sentiment classification (bullish/bearish/neutral) in `backend/tests/integration/test_sentiment_classification.py`
- [ ] **T011** [P] Integration test: weighted scoring calculation in `backend/tests/integration/test_weighted_scoring.py`
- [ ] **T012** [P] Integration test: bot detection scoring in `backend/tests/integration/test_bot_detection.py`
- [ ] **T013** [P] Integration test: historical trend query in `backend/tests/integration/test_historical_trends.py`

## Phase 3.3: Data Layer (ONLY after tests are failing)

### Database Models
- [ ] **T014** [P] Author model in `backend/src/models/author.py` (user_id, username, followers_count, verified, etc.)
- [ ] **T015** [P] Post model in `backend/src/models/post.py` (post_id, text, created_at, author_id FK)
- [ ] **T016** [P] Engagement model in `backend/src/models/engagement.py` (post_id FK, like_count, retweet_count, etc.)
- [ ] **T017** [P] SentimentScore model in `backend/src/models/sentiment_score.py` (post_id FK, algorithm_id, classification, confidence)
- [ ] **T018** [P] BotSignal model in `backend/src/models/bot_signal.py` (post_id FK, score, inputs)
- [ ] **T019** [P] WeightingConfig model in `backend/src/models/weighting_config.py` (version, formulas, multipliers)
- [ ] **T020** [P] DailyAggregate model in `backend/src/models/daily_aggregate.py` (date, topic, algorithm_id, counts, weighted_score)
- [ ] **T021** [P] BatchJob model in `backend/src/models/batch_job.py` (batch_job_id, started_at, status, posts_collected)

### Database Setup
- [ ] **T022** SQLAlchemy engine and session factory in `backend/src/storage/database.py`
- [ ] **T023** Database initialization script (create tables) in `backend/src/storage/init_db.py`

## Phase 3.4: Services & Business Logic

### Data Collection
- [ ] **T024** X API client wrapper in `backend/src/services/x_api_client.py` (search by hashtag, handle rate limits)
- [ ] **T025** Post collector service in `backend/src/services/post_collector.py` (fetch posts, parse metadata, store raw data)
- [ ] **T026** Batch job orchestrator in `backend/src/jobs/daily_batch.py` (run collection, track job status)

### Sentiment Analysis
- [ ] **T027** [P] Sentiment analyzer interface in `backend/src/services/sentiment/base.py` (abstract class for algorithms)
- [ ] **T028** [P] OpenAI sentiment analyzer in `backend/src/services/sentiment/openai_analyzer.py` (bullish/bearish/neutral classification)
- [ ] **T029** [P] FinBERT sentiment analyzer in `backend/src/services/sentiment/finbert_analyzer.py` (local model fallback)
- [ ] **T030** [P] VADER sentiment analyzer in `backend/src/services/sentiment/vader_analyzer.py` (baseline/tertiary)
- [ ] **T031** Sentiment service coordinator in `backend/src/services/sentiment_service.py` (run multiple algorithms, store scores, handle fallback)

### Bot Detection
- [ ] **T032** Bot detection service in `backend/src/services/bot_detector.py` (calculate bot likelihood from author patterns)

### Weighting & Aggregation
- [ ] **T033** Weighting calculator in `backend/src/services/weighting_calculator.py` (apply visibility, influence, verification, bot penalty)
- [ ] **T034** Daily aggregator service in `backend/src/services/daily_aggregator.py` (calculate daily metrics, weighted scores, dominant sentiment)

## Phase 3.5: API Endpoints

- [ ] **T035** GET /health endpoint implementation in `backend/src/api/health.py`
- [ ] **T036** GET /sentiment/trends endpoint in `backend/src/api/sentiment.py` (query daily aggregates, filter by topic/algorithm/date range)
- [ ] **T037** GET /sentiment/daily endpoint in `backend/src/api/sentiment.py` (get specific day aggregate)
- [ ] **T038** API router registration in `backend/src/main.py`

## Phase 3.6: Job Scheduling

- [ ] **T039** APScheduler configuration in `backend/src/jobs/scheduler.py` (daily batch at 23:59)
- [ ] **T040** Bash script `scripts/run_daily_batch.sh` (manual trigger for testing)

## Phase 3.7: Configuration & Error Handling

- [ ] **T041** [P] Config loader in `backend/src/config.py` (load .env, validate required keys)
- [ ] **T042** [P] Logging setup in `backend/src/logging_config.py` (structured logging, file + console)
- [ ] **T043** Error handling middleware in `backend/src/api/middleware.py` (catch exceptions, return proper HTTP errors)
- [ ] **T044** API rate limiting and quota tracking in `backend/src/services/quota_tracker.py`

## Phase 3.8: Polish & Validation

### Unit Tests
- [ ] **T045** [P] Unit tests for bot detection logic in `backend/tests/unit/test_bot_detector.py`
- [ ] **T046** [P] Unit tests for weighting formulas in `backend/tests/unit/test_weighting_calculator.py`
- [ ] **T047** [P] Unit tests for sentiment confidence scoring in `backend/tests/unit/test_sentiment_confidence.py`

### Performance & Validation
- [ ] **T048** Performance test: daily batch completes <1 hour for 500 posts in `backend/tests/performance/test_batch_performance.py`
- [ ] **T049** Performance test: API /sentiment/trends responds <2s for 30-day query in `backend/tests/performance/test_api_performance.py`
- [ ] **T050** Validate sentiment accuracy >70% on manually labeled sample (100 posts) in `backend/tests/validation/test_sentiment_accuracy.py`
- [ ] **T051** Validate bot detection precision >80% in `backend/tests/validation/test_bot_precision.py`

### Documentation
- [ ] **T052** [P] Update `README.md` with setup instructions, architecture overview, API usage
- [ ] **T053** [P] Create `docs/API.md` with endpoint documentation and examples
- [ ] **T054** [P] Create `docs/ALGORITHMS.md` documenting sentiment algorithms and weighting formulas

### Cleanup
- [ ] **T055** Remove code duplication and refactor shared logic
- [ ] **T056** Run quickstart.md validation end-to-end
- [ ] **T057** Final constitution compliance check (all 7 principles validated)

## Dependencies

### Critical Path
1. **Setup (T001-T005)** → Everything else
2. **Tests (T006-T013)** → Implementation (T014+)
3. **Models (T014-T021)** → Database setup (T022-T023) → Services (T024+)
4. **Services (T024-T034)** → API endpoints (T035-T038)
5. **Core implementation (T014-T038)** → Scheduling (T039-T040)
6. **Everything** → Polish (T045-T057)

### Blocking Dependencies
- T022 (database.py) blocks T023 (init_db.py)
- T024 (x_api_client.py) blocks T025 (post_collector.py)
- T025 blocks T026 (daily_batch.py)
- T027 (base.py) blocks T028-T030 (analyzers)
- T028-T030 block T031 (sentiment_service.py)
- T031 blocks T034 (daily_aggregator.py)
- T035-T037 block T038 (router registration)

## Parallel Execution Examples

### Batch 1: Contract Tests (after T005)
```bash
# Run T006-T008 in parallel (different files)
pytest backend/tests/contract/test_health.py &
pytest backend/tests/contract/test_sentiment_trends.py &
pytest backend/tests/contract/test_sentiment_daily.py &
wait
```

### Batch 2: Integration Tests (after T005)
```bash
# Run T009-T013 in parallel (different files)
pytest backend/tests/integration/test_daily_batch.py &
pytest backend/tests/integration/test_sentiment_classification.py &
pytest backend/tests/integration/test_weighted_scoring.py &
pytest backend/tests/integration/test_bot_detection.py &
pytest backend/tests/integration/test_historical_trends.py &
wait
```

### Batch 3: Models (after T013)
```bash
# Create T014-T021 in parallel (different files)
# All models are independent
```

### Batch 4: Sentiment Analyzers (after T027)
```bash
# Create T028-T030 in parallel (different files)
# All implement same interface
```

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **Verify tests fail** before implementing (TDD discipline)
- **Commit after each task** for clean git history
- **Constitution compliance**: Validate principles I-VII throughout
- **Budget tracking**: Monitor LLM API costs during T028 implementation

## Validation Checklist

- [x] All contracts (openapi.yaml endpoints) have corresponding tests (T006-T008)
- [x] All entities (data-model.md) have model tasks (T014-T021)
- [x] All tests (T006-T013) come before implementation (T014+)
- [x] Parallel tasks (marked [P]) are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task

---

**Total Tasks**: 57  
**Estimated Completion**: 3-5 days (with parallel execution)  
**Ready for**: Implementation phase (`/implement` or manual execution)
