# Feature Specification: X Sentiment Analysis System

**Feature Branch**: `001-x-sentiment-analysis`  
**Created**: 2025-10-04  
**Status**: Draft  
**Input**: User description: "X Sentiment Analysis - Sentiment analysis of 'Irresponsibly Long $MSTR' community posts with multi-dimensional weighted scoring, bot detection, and historical trend tracking"  
**Updated**: 2025-10-04 - Focused on MSTR community with Mon/Wed/Fri/Sun collection schedule

---

## User Scenarios & Testing

### Primary User Story

As a cryptocurrency analyst, I want to monitor sentiment trends in the "Irresponsibly Long $MSTR" community by analyzing their X (Twitter) posts 4x per week, so that I can understand how this bullish MSTR investor community's sentiment shifts over time and showcase this analysis publicly as a portfolio credential.

**Weekly Workflow:**
1. System collects top 5 posts from "Irresponsibly Long $MSTR" community on Mon/Wed/Fri/Sun
2. Each post is analyzed for bullish/bearish/neutral sentiment
3. Posts are weighted by visibility (likes, retweets), author influence (followers), verification status, and bot likelihood
4. Daily aggregate sentiment score is calculated and stored
5. User can view historical sentiment trends via API
6. User can compare sentiment results across different analysis algorithms

### Acceptance Scenarios

#### Scenario 1: Community Post Collection
1. **Given** it is a collection day (Monday, Wednesday, Friday, or Sunday)
   **When** the collection script runs
   **Then** system collects top 5 posts from "Irresponsibly Long $MSTR" community (ID: 1761182781692850326) from the past 72 hours with min 2 retweets
   **And** stores complete post metadata (author, engagement metrics, content, timestamps)

#### Scenario 2: Sentiment Classification
2. **Given** a post containing "Bitcoin to the moon! 🚀 $100k incoming"
   **When** sentiment analysis runs
   **Then** post is classified as Bullish with high confidence (>0.8)
   **And** sentiment score is stored with algorithm identifier and version

#### Scenario 3: Weighted Scoring
3. **Given** two posts: Post A (bearish, 1 like) and Post B (bullish, 100 likes)
   **When** daily aggregate sentiment is calculated
   **Then** Post B contributes significantly more weight to the daily sentiment score
   **And** daily sentiment leans bullish

#### Scenario 4: Bot Detection
4. **Given** a post from an account with suspicious patterns (new account, high posting frequency, generic content)
   **When** bot detection runs
   **Then** post is flagged with high bot likelihood score (>0.7)
   **And** post's contribution to sentiment is reduced or excluded

#### Scenario 5: Historical Trend Query
5. **Given** 30 days of collected sentiment data
   **When** user requests sentiment trend for Bitcoin over the past month
   **Then** system returns daily sentiment scores with bullish/bearish/neutral breakdown
   **And** displays trend visualization (line chart)

#### Scenario 6: Algorithm Comparison
6. **Given** sentiment has been analyzed using multiple algorithms (OpenAI, FinBERT, VADER)
   **When** user views sentiment trends
   **Then** system displays separate trend lines for each algorithm
   **And** user can compare how different algorithms scored the same time period

### Edge Cases

**Data Collection:**
- What happens when X API rate limit is reached mid-batch?
  → System pauses, logs quota exhaustion, resumes when quota resets
- What happens when no posts match the search criteria for a day?
  → System logs zero-post day, stores null sentiment score with metadata explaining absence
- What happens when X API returns partial/corrupted data?
  → System validates response, logs errors, stores only valid posts, flags batch as incomplete

**Sentiment Analysis:**
- What happens when a post contains mixed sentiment ("Bitcoin pumping but MSTR dumping")?
  → System assigns dominant sentiment based on algorithm confidence, flags as low-confidence if ambiguous
- What happens when LLM API fails or times out?
  → System falls back to secondary algorithm (local model), logs failure, retries later
- What happens when post is in non-English language?
  → System flags as unsupported language, excludes from analysis (v1.0 English-only)

**Bot Detection:**
- What happens when a verified account exhibits bot-like behavior?
  → Bot detection still runs, but verification status reduces bot likelihood score
- What happens when bot detection is uncertain (score ~0.5)?
  → Post is included but flagged for potential manual review

**Historical Data:**
- What happens when user queries date range with no data?
  → System returns empty result set with clear message "No data available for this period"
- What happens when algorithm version changes and user wants to compare old vs new?
  → System supports reprocessing historical posts with new algorithm, stores both versions

---

## Requirements

### Functional Requirements - Data Collection

- **FR-001**: System MUST collect posts from X API from specific community "Irresponsibly Long $MSTR" (ID: 1761182781692850326) using context: operator
- **FR-002**: System MUST run collection 4x per week on Monday, Wednesday, Friday, Sunday (manual trigger within free tier constraints)
- **FR-003**: System MUST capture complete post metadata: post ID, text, timestamp, author info, engagement metrics (likes, retweets, replies, quotes, bookmarks if available)
- **FR-004**: System MUST capture author metadata: user ID, username, display name, follower count, verification status, account creation date
- **FR-005**: System MUST handle X API rate limiting gracefully (pause, log, resume)
- **FR-006**: System MUST track data lineage: API call timestamp, batch job ID, search query used
- **FR-007**: System MUST validate API responses and reject corrupted/incomplete data
- **FR-008**: System MUST work within X API Free Tier constraints (100 tweets/month read limit, collecting 5 posts per run = ~85 tweets/month)

### Functional Requirements - Sentiment Analysis

- **FR-009**: System MUST classify each post as Bullish, Bearish, or Neutral (not generic positive/negative)
- **FR-010**: System MUST support multiple sentiment analysis algorithms (LLM-based, traditional ML, rule-based)
- **FR-011**: System MUST store sentiment score with confidence level (0-1 scale)
- **FR-012**: System MUST track which algorithm and version generated each sentiment score
- **FR-013**: System MUST support algorithm fallback (if primary fails, use secondary)
- **FR-014**: System MUST handle mixed sentiment posts (assign dominant sentiment, flag low confidence)
- **FR-015**: System MUST exclude non-English posts from analysis (v1.0 constraint)
- **FR-016**: System MUST allow reprocessing historical posts with updated algorithms

### Functional Requirements - Bot Detection

- **FR-017**: System MUST assign bot likelihood score (0-1) to each post based on author patterns
- **FR-018**: Bot detection MUST consider: account age, posting frequency, follower/following ratio, profile completeness, content patterns
- **FR-019**: System MUST reduce or exclude high bot-likelihood posts (>0.7) from sentiment aggregation
- **FR-020**: System MUST preserve bot detection scores for audit and refinement
- **FR-021**: Bot detection MUST achieve >80% precision (low false positives)

### Functional Requirements - Weighted Scoring

- **FR-022**: System MUST weight sentiment by post visibility (likes, retweets, views)
- **FR-023**: System MUST weight sentiment by author influence (follower count)
- **FR-024**: System MUST weight sentiment by verification status (verified accounts carry more weight)
- **FR-025**: System MUST apply bot likelihood as negative weight (reduce bot post influence)
- **FR-026**: Weighting formulas MUST be configurable (not hardcoded)
- **FR-027**: System MUST track which weighting version was used for each calculation

### Functional Requirements - Daily Aggregates

- **FR-028**: System MUST calculate aggregate sentiment score for MSTR community (focused on single topic)
- **FR-029**: System MUST store daily metrics: total posts, bullish count, bearish count, neutral count, percentages
- **FR-030**: System MUST store daily engagement aggregates: total likes, retweets, average engagement per post
- **FR-031**: System MUST identify dominant sentiment for the day (Bullish/Bearish/Neutral)
- **FR-032**: System MUST store separate daily aggregates per algorithm (enable comparison)
- **FR-033**: System MUST track quality metrics: bot detection rate, high-confidence sentiment %, posts requiring review

### Functional Requirements - Historical Tracking

- **FR-034**: System MUST retain raw post data for minimum 1 year
- **FR-035**: System MUST retain daily aggregates indefinitely
- **FR-036**: System MUST support querying sentiment trends over arbitrary date ranges
- **FR-037**: System MUST support filtering trends by topic, algorithm, date range
- **FR-038**: System MUST generate trend visualizations (line charts, bar charts)

### Functional Requirements - Web Interface

- **FR-039**: System MUST expose API endpoints for querying sentiment data
- **FR-040**: System MUST provide web interface displaying sentiment trends
- **FR-041**: System MUST allow users to compare algorithm results side-by-side
- **FR-042**: System MUST display daily metrics (post counts, sentiment breakdown)
- **FR-043**: System MUST show top engaged posts for each day
- **FR-044**: Web interface MUST be publicly accessible (portfolio credential requirement)

### Functional Requirements - Data Management

- **FR-045**: System MUST store data locally (SQLite for development)
- **FR-046**: System MUST support migration to PostgreSQL for production deployment
- **FR-047**: System MUST implement database schema versioning
- **FR-048**: System MUST support schema evolution without breaking changes
- **FR-049**: System MUST log all batch job executions (start time, end time, posts collected, errors)

### Non-Functional Requirements

- **NFR-001**: Daily batch job MUST complete within 1 hour (for 500 posts)
- **NFR-002**: API endpoints MUST respond within 2 seconds for trend queries (30-day range)
- **NFR-003**: System MUST handle X API quota exhaustion without data loss
- **NFR-004**: LLM API costs MUST stay within $50/month budget
- **NFR-005**: Bot detection MUST achieve >80% precision (minimize false positives)
- **NFR-006**: Sentiment algorithms MUST be validated against manually labeled sample (min 100 posts)
- **NFR-007**: System MUST be deployable to cloud (web-ready architecture)
- **NFR-008**: All data processing functions MUST have unit tests
- **NFR-009**: API endpoints MUST have integration tests

### Out of Scope (v1.0)

- Real-time streaming analysis (deferred to v2.0)
- Emotion detection beyond bullish/bearish/neutral
- Aspect-based sentiment (sentiment per entity within post)
- Sarcasm detection
- Multi-language support (English only for v1.0)
- User authentication/authorization for web UI
- Automated trading signals or recommendations
- Integration with market price data

---

## Key Entities

### Post
Represents a single X (Twitter) post collected for analysis.
- **Attributes**: post ID, text content, creation timestamp, language, media attachments
- **Relationships**: belongs to one Author, has multiple Engagement Metrics, has multiple Sentiment Scores (one per algorithm)

### Author
Represents the X user who created a post.
- **Attributes**: user ID, username, display name, follower count, following count, verification status, account creation date, profile description
- **Relationships**: has many Posts
- **Derived**: bot likelihood score (calculated from attributes and behavior patterns)

### Sentiment Score
Represents the sentiment analysis result for a post.
- **Attributes**: sentiment classification (Bullish/Bearish/Neutral), confidence score (0-1), algorithm identifier, algorithm version, processing timestamp
- **Relationships**: belongs to one Post

### Engagement Metrics
Represents the visibility and reach of a post.
- **Attributes**: like count, retweet count, reply count, quote count, bookmark count (optional), impression count (optional), view count (optional)
- **Relationships**: belongs to one Post
- **Usage**: Used for weighted sentiment scoring

### Daily Aggregate
Represents the aggregated sentiment for a specific topic on a specific day.
- **Attributes**: date, topic (Bitcoin/MSTR/Bitcoin treasuries), algorithm identifier, total posts, bullish count, bearish count, neutral count, weighted sentiment score, dominant sentiment, quality metrics
- **Relationships**: aggregates many Posts
- **Derived**: calculated from individual post sentiment scores and weights

### Batch Job
Represents a single execution of the daily data collection process.
- **Attributes**: batch job ID, start timestamp, end timestamp, status (running/completed/failed), posts collected count, errors encountered
- **Relationships**: collects many Posts
- **Usage**: Data lineage tracking and debugging

### Weighting Configuration
Represents the formula and parameters used for weighted sentiment scoring.
- **Attributes**: version identifier, visibility weight formula, influence weight formula, verification weight multiplier, bot penalty formula, effective date
- **Usage**: Enables iterative refinement of weighting algorithms, supports A/B testing

---

## Dependencies & Assumptions

### External Dependencies
- **X API v2**: Free tier access (100 tweets/month read limit), requires API credentials
- **LLM API**: OpenAI or Anthropic API for primary sentiment analysis, requires API key and budget ($50/month) - Currently using keyword-based placeholder
- **Local ML Models**: Hugging Face transformers for fallback sentiment analysis (FinBERT, crypto-specific models)

### Assumptions
- X API Free Tier is sufficient for focused community tracking (100 tweets/month = 5 posts × 4 days/week × 4 weeks = ~80-85 tweets/month)
- Upgrade to X API Basic tier ($100/month) required for larger scale (10,000 tweets/month)
- Community search (context: operator) captures posts from "Irresponsibly Long $MSTR" community
- English-only posts are sufficient for v1.0 (majority of crypto discussion)
- Mon/Wed/Fri/Sun collection schedule is acceptable (real-time not required)
- Bot detection heuristics can achieve >80% precision without ML model
- Keyword-based sentiment is acceptable for MVP, LLM upgrade provides better accuracy

### Constraints
- Budget: $0/month (free tier only for MVP)
- X API: Free tier limits (100 tweets/month read, 500 tweets/month write)
- Collection: 5 posts per run, 4x per week = ~85 tweets/month
- Language: English only (v1.0)
- Deployment: Local development initially, cloud deployment for public showcase

---

## Success Criteria

### Minimum Viable Product (MVP)
- ✅ Daily batch collection runs successfully for 7 consecutive days
- ✅ Sentiment classification achieves >70% accuracy on manually labeled sample (100 posts)
- ✅ Bot detection achieves >80% precision (validated against known bot accounts)
- ✅ Historical trend data is queryable and visualizable
- ✅ Web interface displays sentiment trends publicly
- ✅ At least 2 algorithms are compared side-by-side

### Quality Gates
- All functional requirements (FR-001 to FR-049) are implemented and tested
- All non-functional requirements (NFR-001 to NFR-009) are met
- No [NEEDS CLARIFICATION] markers remain in specification
- Constitution principles are validated and enforced

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs) - tech stack in constitution, not spec
- [x] Focused on user value and business needs - portfolio credential, market insight
- [x] Written for non-technical stakeholders - clear user scenarios
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous - all FRs have clear acceptance criteria
- [x] Success criteria are measurable - accuracy %, precision %, completion metrics
- [x] Scope is clearly bounded - v1.0 scope and out-of-scope items defined
- [x] Dependencies and assumptions identified - X API, LLM API, budget constraints

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted - sentiment analysis, bot detection, weighted scoring, historical tracking
- [x] Ambiguities marked - none remaining, all clarified through constitution
- [x] User scenarios defined - 6 acceptance scenarios, edge cases covered
- [x] Requirements generated - 49 functional requirements, 9 non-functional requirements
- [x] Entities identified - 7 key entities with relationships
- [x] Review checklist passed - all items validated

---

**Status**: ✅ Ready for Planning Phase (`/plan`)
