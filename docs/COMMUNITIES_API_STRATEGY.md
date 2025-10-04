# X Communities API Strategy

## Free Tier Limits (Confirmed from X API Docs)

### Communities Endpoints Available

**1. GET /2/communities/:id** (Get specific community)
- **Free Limit:** 1 request / 15 mins (per user)
- **Per App:** 1 request / 15 mins
- **Usage:** Get community details, member count, rules

**2. GET /2/communities/search** (Search for communities)
- **Free Limit:** 1 request / 15 mins (per user)
- **Per App:** 1 request / 15 mins
- **Returns:** Up to 100 results per response
- **Usage:** Find community by name/keywords

### Tweet Reading Limits
- **100 tweets/month** (separate from community lookups)
- Used for actual post collection

---

## Target Community

**Name:** "Irresponsibly Long $MSTR"

**Why This Community:**
- ✅ Focused MSTR investor community
- ✅ Clear bullish bias ("Irresponsibly Long")
- ✅ Higher quality than general hashtags
- ✅ Consistent activity
- ✅ Real investors, not spam

---

## Proposed Collection Strategy

### Phase 1: One-Time Setup (2 API calls)

**Step 1: Find Community ID**
```python
GET /2/communities/search?query="Irresponsibly Long MSTR"
# Returns: community_id, name, description
# Cost: 1 API call (separate quota)
```

**Step 2: Verify Community**
```python
GET /2/communities/{community_id}
# Returns: member_count, rules, admin_results
# Cost: 1 API call (separate quota)
```

### Phase 2: Regular Collection

**Frequency:** Mon/Wed/Fri/Sun (4 days per week)

**Schedule:**
- Monday: Start of week, market open
- Wednesday: Mid-week activity
- Friday: End of week, pre-weekend
- Sunday: Weekend sentiment before Monday market

**Per Collection:**
```python
# Search tweets from community
query = f"context:{community_id}"
# Or: query = f"conversation_id:{community_id}"
max_results = 5  # Top 5 posts

# Filters to add:
# - Sort by engagement
# - English only
# - No retweets
```

**Monthly Usage:**
- 4 collections/week × 4.3 weeks = ~17 collections/month
- 17 collections × 5 tweets = **85 tweets/month**
- Buffer: 15 tweets for testing/adjustments
- Total: Under 100 tweet limit ✅

**Example October Schedule:**
```
Week 1: Mon 7, Wed 9, Fri 11, Sun 13
Week 2: Mon 14, Wed 16, Fri 18, Sun 20
Week 3: Mon 21, Wed 23, Fri 25, Sun 27
Week 4: Mon 28, Wed 30
= 14 collections in October
```

---

## Implementation Plan

### Script 1: `find_community.py`
- Search for "Irresponsibly Long $MSTR"
- Get community ID
- Save to config file
- **Run once**

### Script 2: `collect_community_posts.py`
- Read community ID from config
- Collect top 5 posts from community
- Store in database
- Track quota usage
- **Run every other day**

### Script 3: `collection_log.csv`
- Track collection dates
- Monitor quota usage
- Prevent over-collection

---

## Data Quality Benefits

**vs. Hashtag Search:**
- ❌ Hashtags: Spam, bots, random mentions
- ✅ Community: Verified members, focused discussion

**vs. General MSTR:**
- ❌ General: Mixed sentiment, news, critics
- ✅ Community: Consistent bullish perspective

**Analysis Opportunities:**
- Track sentiment intensity within bull community
- Identify when bulls turn cautious
- Correlation with MSTR stock price
- Community engagement trends

---

## Questions for Refinement

1. **Community Identification:**
   - Exact community name?
   - Is it public or private?
   - Backup communities if not found?

2. **Post Selection Criteria:**
   - Most liked?
   - Most retweeted?
   - Most recent?
   - Combination of engagement metrics?

3. **Time Window:**
   - Last 48 hours (since last collection)?
   - Last 24 hours?
   - Last week?

4. **Automation:**
   - Manual collection (set reminders)?
   - Automated cron job?
   - Cloud deployment?

5. **Analysis Goals:**
   - Just sentiment tracking?
   - Correlation with stock price?
   - Community growth tracking?
   - Engagement trends?

---

## Next Steps

1. ✅ Confirm exact community name
2. ⏳ Create `find_community.py` script
3. ⏳ Test community search
4. ⏳ Create `collect_community_posts.py` script
5. ⏳ Set up collection schedule
6. ⏳ Define post selection criteria
7. ⏳ Create monitoring dashboard

---

## Notes

- Community API quota is SEPARATE from tweet reading quota
- Failed requests don't count against quota
- Rate limits reset every 15 minutes
- Can search multiple communities if needed
- Consider tracking multiple MSTR communities for comparison

---

**Status:** Strategy defined, ready for implementation  
**Date:** 2025-10-04  
**Free Tier:** 100 tweets/month confirmed
