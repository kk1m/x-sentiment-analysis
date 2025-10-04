#!/bin/bash
# Manual trigger for daily batch job
# Usage: ./scripts/run_daily_batch.sh [--dry-run]

set -e

cd "$(dirname "$0")/.."

if [ "$1" == "--dry-run" ]; then
    echo "🔍 DRY RUN MODE - No actual API calls will be made"
    echo ""
fi

echo "🚀 Running daily batch job..."
echo "   Time: $(date)"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the batch job
python -c "
import asyncio
from backend.src.jobs.daily_batch import run_daily_batch

async def main():
    batch_job_id = await run_daily_batch()
    print(f'\n✅ Batch job completed: {batch_job_id}')

asyncio.run(main())
"

echo ""
echo "✓ Daily batch job completed"
echo ""
echo "📊 Run aggregation:"
echo "   python run_aggregator.py"
