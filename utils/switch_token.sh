#!/bin/bash
# Switch between MAIN and BACKUP X API tokens

if [ "$1" == "main" ]; then
    echo "🔄 Switching to MAIN token..."
    # Get current main token from .env
    echo "✅ Switched to MAIN token (keeping current)"
elif [ "$1" == "backup" ]; then
    echo "🔄 Switching to BACKUP token..."
    # Update .env to use backup token (URL decoded)
    sed -i '' 's/^X_API_KEY=.*$/X_API_KEY=AAAAAAAAAAAAAAAAAAAAAKhz4gEAAAAAL\/2tFLi1pjz5kfhpzvgl8OM\/QUs=jVjWo0S5MAPvVl5PqXShXOAAZ4B7I09LlzFPpuKCyuQ7IETgcm/' .env
    echo "✅ Switched to BACKUP token"
else
    echo "Usage: ./switch_token.sh [main|backup]"
    echo ""
    echo "Current token in .env:"
    grep "^X_API_KEY=" .env | head -c 50
    echo "..."
fi
