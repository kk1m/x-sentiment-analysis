# Community Collection Workflow

## 🎯 Goal
Collect top 5 posts from "Irresponsibly Long $MSTR" community on Mon/Wed/Fri/Sun

## 📋 One-Time Setup

### Step 1: Find Community ID
```bash
python find_community.py
```

**What it does:**
- Searches X API for "Irresponsibly Long $MSTR" community
- Displays all matching communities
- Saves community ID to `community_config.json`

**Expected output:**
```
✓ Found 1 communities

1. Irresponsibly Long $MSTR
   ID: 1234567890
   Description: ...

✅ Community ID saved to community_config.json
```

**Run this ONCE** - the ID is saved for future collections

---

## 🔄 Regular Collection (Mon/Wed/Fri/Sun)

### Step 2: Collect Posts
```bash
python collect_community_posts.py
```

**What it does:**
- Reads community ID from `community_config.json`
- Collects top 5 posts from the community
- Stores posts, authors, and engagement in database
- Logs collection to `collection_log.csv`
- Shows quota usage

**Expected output:**
```
🎯 Collecting posts from 'Irresponsibly Long $MSTR' community...
📍 Community: Irresponsibly Long $MSTR
   ID: 1234567890

✓ Found 5 posts

[1] @username1
    Bitcoin to the moon! MSTR accumulating...
    ❤️  45 | 🔁 12 | 💬 8

[2] @username2
    ...

✅ Stored 5 posts in database
💰 Quota: 5 tweets used, ~95 remaining this month
```

---

## 📊 Analysis Workflow

### Step 3: Analyze Sentiment
```bash
python analyze_posts.py
```

**What it does:**
- Finds unanalyzed posts
- Runs sentiment classification (Bullish/Bearish/Neutral)
- Runs bot detection
- Stores results in database

---

### Step 4: Create Daily Aggregate
```bash
python run_aggregator.py
```

**What it does:**
- Aggregates all posts for today
- Calculates weighted sentiment score
- Stores in `daily_aggregates` table

---

### Step 5: View Results
```bash
curl "http://localhost:8000/sentiment/trends?topic=MSTR&days=7"
```

**Or visit:** http://localhost:8000/docs

---

## 📅 Collection Schedule

### Recommended Calendar Reminders

**Monday 9:00 PM:**
```
python collect_community_posts.py
python analyze_posts.py
python run_aggregator.py
```

**Wednesday 9:00 PM:**
```
python collect_community_posts.py
python analyze_posts.py
python run_aggregator.py
```

**Friday 9:00 PM:**
```
python collect_community_posts.py
python analyze_posts.py
python run_aggregator.py
```

**Sunday 9:00 PM:**
```
python collect_community_posts.py
python analyze_posts.py
python run_aggregator.py
```

---

## 📈 Tracking Progress

### View Collection Log
```bash
cat collection_log.csv
```

**Example:**
```
date,day_of_week,posts_collected,cumulative_total
2025-10-07,Monday,5,5
2025-10-09,Wednesday,5,10
2025-10-11,Friday,5,15
2025-10-13,Sunday,5,20
```

### Check Quota Usage
```bash
tail -1 collection_log.csv
```

Shows cumulative tweets collected this month

---

## 🔧 Troubleshooting

### "Community not found"
- Verify community name spelling
- Check if community is public (not private)
- Try searching on X directly: https://twitter.com/i/communities

### "Rate limit exceeded"
- Wait 15-30 minutes
- Failed requests don't count against quota
- Try again later

### "No posts found"
- Community might have no recent activity
- Try adjusting query in `collect_community_posts.py`
- Remove `-is:retweet` filter temporarily

### "Module not found"
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 Monthly Workflow

**Week 1:** 4 collections (Mon/Wed/Fri/Sun) = 20 tweets  
**Week 2:** 4 collections = 20 tweets  
**Week 3:** 4 collections = 20 tweets  
**Week 4:** 4 collections = 20 tweets  
**Total:** ~80 tweets (20 tweet buffer)

---

## 🎯 Success Metrics

After 1 month, you should have:
- ✅ ~80-85 MSTR community posts
- ✅ 16-17 data points (collections)
- ✅ Sentiment trend over 4 weeks
- ✅ Engagement patterns
- ✅ Community sentiment analysis

---

## 🚀 Next Steps

1. **Set calendar reminders** for Mon/Wed/Fri/Sun 9pm
2. **Run find_community.py** to get community ID
3. **Test first collection** on next scheduled day
4. **Monitor quota** via collection_log.csv
5. **Analyze trends** after 2 weeks of data
