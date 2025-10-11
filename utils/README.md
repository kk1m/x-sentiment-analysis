# Utility Scripts

This directory contains helper scripts for data collection, analysis, and testing.

## Data Collection
- **`collect_small_batch.py`** - Collect a small batch of MSTR tweets (respects free tier limits)
- **`collect_community_posts.py`** - Collect posts from community configuration

## Analysis & Processing
- **`analyze_posts.py`** - Run sentiment analysis and bot detection on collected posts
- **`view_today_analysis.py`** - View analysis summary for posts collected today
- **`run_aggregator.py`** - Run sentiment aggregation
- **`run_aggregator_bulk.py`** - Bulk sentiment aggregation

## Testing & Demos
- **`test_x_api.py`** - Test X API connection
- **`test_community_query.py`** - Test community query functionality
- **`demo.py`** - Demo script
- **`demo_20_posts.py`** - Demo with 20 posts
- **`demo_quarterly.py`** - Quarterly demo

## Utilities
- **`find_community.py`** - Find community posts
- **`view_api_logs.py`** - View API logs

## Usage

All scripts should be run from the project root directory:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run a script
python utils/collect_small_batch.py
python utils/analyze_posts.py
python utils/view_today_analysis.py
```
