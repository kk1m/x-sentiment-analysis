# Quick Start - When Rate Limit Clears

## 🚀 Complete End-to-End Workflow

Run these commands in order to see the entire system work:

**Note:** Community ID is already hardcoded (1761182781692850326), so you can skip Step 1.

### Step 1: Find Community (OPTIONAL - Already Done)
```bash
python find_community.py
```
**Purpose:** Search for community and save ID  
**Status:** ✅ Already done - community_config.json exists  
**Skip this:** Community ID is already hardcoded

### Step 2: Test Community Query (Optional)
```bash
python test_community_query.py
```
**Purpose:** Verify the `context:` operator works  
**Expected:** Should find 5 posts from "Irresponsibly Long $MSTR" community  
**Uses:** 5 of your 100 tweets/month  

---

### Step 3: Collect Community Posts
```bash
python collect_community_posts.py
```
**What it does:**
- Searches community ID: 1761182781692850326
- Collects top 5 posts from last 72 hours
- Filters: min 2 retweets, no retweets, English
- Stores in database (authors, posts, engagement)
- Logs to collection_log.csv

**Expected output:**
```
✓ Found 5 posts

[1] @username
    Post text preview...
    ❤️  45 | 🔁 12 | 💬 8

✅ Stored 5 posts in database
💰 Quota: 5 tweets used, ~95 remaining
```

---

### Step 4: Analyze Sentiment
```bash
python analyze_posts.py
```
**What it does:**
- Finds unanalyzed posts
- Classifies sentiment (Bullish/Bearish/Neutral)
- Calculates confidence (0-1)
- Detects bots (0-1 score)
- Stores results

**Expected output:**
```
[1/5] Analyzing post...
   Sentiment: Bullish (0.85)
   Bot score: 0.12

✅ Analysis complete!
```

---

### Step 5: Create Daily Aggregate
```bash
python run_aggregator.py
```
**What it does:**
- Aggregates all posts for today
- Calculates weighted sentiment score
- Applies multi-factor weighting (engagement × influence × verification × bot penalty)
- Stores in daily_aggregates table

**Expected output:**
```
✅ Daily aggregate created for 2025-10-04
   Topic: MSTR
   Total posts: 5
   Bullish: 4 (80.0%)
   Bearish: 1 (20.0%)
   Weighted score: 0.673
   Dominant sentiment: Bullish
```

---

### Step 6: View Results via API
```bash
# Start API server (if not running)
python -m uvicorn backend.src.main:app --reload

# In another terminal, query the API:
curl "http://localhost:8000/sentiment/trends?topic=MSTR&days=1"
```

**Or visit:** http://localhost:8000/docs

---

## 📊 What You'll Have After First Run

- ✅ 5 real posts from "Irresponsibly Long $MSTR" community
- ✅ Sentiment analysis (Bullish/Bearish/Neutral)
- ✅ Bot detection scores
- ✅ Weighted aggregate sentiment
- ✅ API endpoint with results
- ✅ 5 tweets used, 95 remaining

---

## 📅 Regular Collection Schedule

**Set calendar reminders for:**
- **Monday 9:00 PM**
- **Wednesday 9:00 PM**
- **Friday 9:00 PM**
- **Sunday 9:00 PM**

**Run these 3 commands:**
```bash
python collect_community_posts.py
python analyze_posts.py
python run_aggregator.py
```

**After 1 month:**
- ~17 collections
- ~85 tweets analyzed
- 4 weeks of MSTR community sentiment trends
- Portfolio-ready visualization data

---

## 🔧 Troubleshooting

### "Rate limit exceeded"
- Wait 15-30 minutes
- Failed requests don't count against quota
- Try again later

### "No posts found"
- Community might have no posts in last 72 hours
- Try removing `min_retweets:2` filter temporarily
- Check if community is active

### "context: operator invalid"
- Free tier might not support community queries
- Fallback: Use phrase search `"Irresponsibly Long" MSTR`
- Consider upgrading to Basic tier ($100/month)

---

## 💰 Quota Tracking

**Check usage:**
```bash
tail -1 collection_log.csv
```

**View all collections:**
```bash
cat collection_log.csv
```

---

## 🎯 Success Criteria

After first successful run, you should see:
- ✅ 5 rows in `posts` table
- ✅ 5 rows in `authors` table
- ✅ 5 rows in `engagements` table
- ✅ 5 rows in `sentiment_scores` table
- ✅ 5 rows in `bot_signals` table
- ✅ 1 row in `daily_aggregates` table
- ✅ 1 row in `collection_log.csv`

**Verify:**
```bash
sqlite3 sentiment_analysis.db "SELECT COUNT(*) FROM posts;"
sqlite3 sentiment_analysis.db "SELECT * FROM daily_aggregates;"
```

---

## 🚀 You're Ready!

Everything is configured and ready to go. Just wait for the rate limit to clear and run the workflow!

**Repository:** https://github.com/kk1m/x-sentiment-analysis
