# Collection Service Consolidation

## Problem Identified
- **3 duplicate collection implementations** with different queries and filters
- **96% of collected tweets were spam/retweets** due to missing filters
- **Inconsistent behavior** across different collection scripts

## Solution: TweetCollector Service

### Single Source of Truth
**File:** `backend/src/services/tweet_collector.py` (renamed from `post_collector.py`)

### Standard Query (MSTR_QUERY)
```
#MSTR (MicroStrategy OR Saylor OR Bitcoin OR BTC OR crypto OR price OR market OR stock OR shares OR treasury OR strategy OR bullish OR bearish OR buy OR sell OR hodl OR rally OR dump OR crash OR moon) -is:retweet -is:reply lang:en -giveaway -"giving away" -"will receive" -"follow me" -"DM to own"
```

### Standard Settings
- **Batch size:** 10 tweets (free tier limit)
- **Metrics captured:**
  - Author: user_id, username, display_name, profile_description, followers_count, following_count, verified, created_at
  - Post: post_id, author_id, text, language, created_at, has_media, collected_at, batch_job_id
  - Engagement: like_count, retweet_count, reply_count, quote_count

### Files Updated

**Service:**
- ✅ `backend/src/services/post_collector.py` → `backend/src/services/tweet_collector.py`
  - Renamed `PostCollector` → `TweetCollector`
  - Added standard `MSTR_QUERY` with all filters
  - **Built-in logging** to CSV (automatic)
  - **Built-in error handling** with rate limit messages
  - API: `collect_and_store_posts(since, batch_job_id, max_results, query, log, verbose)`

**Jobs:**
- ✅ `backend/src/jobs/daily_batch.py` - Updated to use `TweetCollector`

**Utilities:**
- ✅ `utils/collect_small_batch.py` - **DELETED** (functionality moved to TweetCollector)
- ✅ `utils/collect_tweets.py` - **NEW** Simple wrapper script for manual collection
- ⚠️ `utils/collect_community_posts.py` - Still has duplicate logic (needs update)

### Benefits
1. **Single query definition** - Change once, applies everywhere
2. **Consistent quality** - All collections use same filters
3. **Less code** - Removed ~200 lines of duplication
4. **Easier maintenance** - One place to fix bugs or add features

### Next Steps
- [ ] Update `utils/collect_community_posts.py` to use `TweetCollector`
- [ ] Update tests to use `TweetCollector`
- [ ] Remove old `should_filter_post()` function (no longer needed)
- [ ] Test collection with new service

### Usage

**Option 1: Use the convenience script**
```bash
python utils/collect_tweets.py
```

**Option 2: Use TweetCollector directly in Python**
```python
import asyncio
from datetime import datetime, timedelta
from backend.src.services.tweet_collector import TweetCollector

async def main():
    collector = TweetCollector()
    since = datetime.utcnow() - timedelta(hours=2)
    
    posts = await collector.collect_and_store_posts(
        since=since,
        max_results=10,
        verbose=True  # Show output and errors
    )
    print(f"Collected {posts} posts")

asyncio.run(main())
```

**Verify quality:**
```bash
python utils/view_today_analysis.py
```
