<!--
Sync Impact Report:
- Version: Initial → 1.1.0
- New constitution created for X Sentiment Analysis project
- Added Principle VII: Complete Data Capture (MINOR version bump)
- Clarified scope: daily metrics and post metadata storage requirements
- Templates: ⚠ pending review for alignment with principles
- Follow-up: Review plan-template.md, spec-template.md, tasks-template.md for consistency
-->

# X Sentiment Analysis Constitution

## Core Principles

### I. Signal Quality Over Noise (NON-NEGOTIABLE)
**Bot detection and signal filtering are critical to project success.**

- MUST implement bot detection mechanisms to filter out artificial engagement
- MUST weight sentiment by genuine engagement metrics (likes, retweets, views)
- MUST distinguish between organic and inorganic activity
- Bot detection algorithms MUST be continuously refined as bot behavior evolves
- False positives (marking real users as bots) are acceptable; false negatives (missing bots) undermine the entire analysis

**Rationale**: Sophisticated entities deploy bot networks to manipulate sentiment. Without robust bot filtering, the analysis becomes meaningless noise rather than actionable signal.

### II. Multi-Dimensional Weighted Analysis
**Sentiment scoring MUST account for post visibility, author influence, and verification status.**

- Post visibility (likes, retweets, views) MUST influence sentiment weight
- Author influence (follower count) MUST be factored into scoring
- Verification status MUST be tracked as a trust signal
- Weighting algorithms MUST be configurable and updatable
- A single high-visibility post MUST outweigh multiple low-visibility posts in aggregate sentiment

**Rationale**: Not all posts are equal. A bearish post with 1 like should not cancel out a bullish post with 100 likes. Visibility reflects market attention and impact.

### III. Algorithm Flexibility & Comparison
**Multiple sentiment algorithms MUST be supported and comparable.**

- System MUST support pluggable sentiment analysis algorithms (LLM-based, traditional ML, rule-based)
- MUST enable side-by-side comparison of different algorithms on the same dataset
- MUST track which algorithm generated which sentiment score
- MUST support A/B testing and iterative refinement of algorithms
- Default to LLM API (OpenAI/Anthropic) but allow fallback to local models

**Rationale**: Sentiment analysis is not a solved problem. Different algorithms have different strengths. Comparison enables continuous improvement and validation.

### IV. Batch Processing & Historical Tracking
**Daily batch analysis with long-term trend visibility.**

- MUST process posts in daily batches (end-of-day aggregation)
- MUST maintain historical sentiment data for trend analysis
- MUST support querying sentiment trends over arbitrary time ranges
- Real-time processing is OUT OF SCOPE for initial version
- Data retention MUST support at least 1 year of historical analysis

**Rationale**: Daily batch processing is sufficient for trend analysis and significantly simpler than real-time streaming. Historical data enables pattern recognition and validation.

### V. Web-Ready Architecture
**Design for eventual public deployment as portfolio credential.**

- MUST use technology stack compatible with web deployment (API + frontend)
- MUST separate data collection, analysis, and presentation layers
- MUST design API endpoints for external consumption
- MUST consider data privacy and API rate limiting for public exposure
- Local development MUST mirror production architecture

**Rationale**: This project will be showcased publicly. Architecture decisions must support both local iteration and eventual cloud deployment.

### VI. Iterative Refinement
**Models, weights, and algorithms MUST be updatable without system redesign.**

- Sentiment models MUST be versioned and swappable
- Weighting formulas MUST be configurable (not hardcoded)
- MUST track which model/weight version generated which results
- MUST support reprocessing historical data with updated models
- Configuration changes MUST be logged and auditable

**Rationale**: Sentiment analysis improves through iteration. The system must support experimentation without requiring rewrites.

### VII. Complete Data Capture
**All post metadata and daily metrics MUST be stored for analysis and debugging.**

- MUST capture complete post metadata: author info, engagement metrics, content, timestamps
- MUST store daily aggregate metrics: total posts, bullish/bearish/neutral counts
- MUST preserve raw data for reprocessing with updated algorithms
- MUST track data lineage: which API call, which batch job, which algorithm version
- Data schema MUST support future metric additions without breaking changes

**Rationale**: Incomplete data prevents retrospective analysis and debugging. Storing comprehensive metadata enables weight tuning, algorithm validation, and future feature development.

## Technical Stack

### Required Technologies
- **Language**: Python 3.10+
- **Data Storage**: SQLite for local development, PostgreSQL-ready for production
- **Data Processing**: pandas, numpy for data manipulation
- **Sentiment Analysis**: 
  - Primary: OpenAI/Anthropic API for LLM-based sentiment
  - Secondary: transformers (Hugging Face) for local models (e.g., FinBERT, crypto-specific models)
  - Tertiary: VADER or TextBlob as baseline/fallback
- **X API**: tweepy or httpx for X API v2 (Free tier compatible)
- **Web Framework**: FastAPI for API layer (future web deployment)
- **Visualization**: matplotlib/plotly for trend charts, Streamlit or React for web UI
- **Scheduling**: APScheduler or cron for daily batch jobs
- **Testing**: pytest, pytest-mock

### API & Cost Constraints
- MUST work with X API Free Tier initially (500 tweets/month limit)
- MUST implement rate limiting and quota tracking
- MUST gracefully handle API quota exhaustion
- LLM API costs MUST be monitored and capped (budget: $50/month initial)
- MUST support local model fallback if API costs exceed budget

## Scope Definition

### In Scope (v1.0)
- Daily batch collection of posts on: Bitcoin, MSTR, Bitcoin treasuries (hashtag-based)
- Bullish/Bearish/Neutral sentiment classification (not generic positive/negative)
- Multi-dimensional weighting: visibility, follower count, verification, bot-likelihood
- Historical trend tracking and visualization
- Multiple algorithm comparison (LLM vs traditional ML)
- Local SQLite storage
- Basic web API for data access
- **Daily aggregate metrics**: total post count, bullish count, bearish count, neutral count
- **Post metadata storage**: user info, engagement metrics (likes, retweets, bookmarks), post content, timestamps

### Out of Scope (v1.0)
- Real-time streaming analysis
- Emotion detection beyond bullish/bearish
- Aspect-based sentiment (sentiment per entity within a post)
- Sarcasm detection (defer to v2.0)
- Multi-language support (English only for v1.0)
- User authentication/authorization for web UI
- Automated trading signals or recommendations

### Future Considerations (v2.0+)
- Expand to broader topics/hashtags beyond crypto
- Real-time sentiment streaming
- Advanced NLP: sarcasm, aspect-based sentiment
- Automated anomaly detection (sudden sentiment shifts)
- Integration with market data (price correlation analysis)

## Development Workflow

### Iteration Cycle
1. **Local Development**: Rapid iteration with SQLite and sample data
2. **Algorithm Testing**: Compare sentiment algorithms on same dataset
3. **Weight Tuning**: Adjust visibility/influence weights based on results
4. **Validation**: Manual review of high-impact posts for accuracy
5. **Deployment Prep**: Migrate to PostgreSQL, containerize, deploy to cloud

### Quality Gates
- All data processing functions MUST have unit tests
- Sentiment algorithms MUST be validated against manually labeled sample set (min 100 posts)
- Bot detection MUST achieve >80% precision (low false positives)
- API endpoints MUST have integration tests
- Daily batch jobs MUST have error handling and retry logic

## Governance

### Amendment Process
- Constitution changes require documented rationale and impact analysis
- Version increments follow semantic versioning:
  - **MAJOR**: Breaking changes to core principles or scope
  - **MINOR**: New principles or significant expansions
  - **PATCH**: Clarifications, wording improvements

### Compliance
- All feature development MUST align with core principles
- Principle violations MUST be explicitly justified and documented
- Bot detection quality is non-negotiable and supersedes performance optimization

**Version**: 1.1.0 | **Ratified**: 2025-10-04 | **Last Amended**: 2025-10-04