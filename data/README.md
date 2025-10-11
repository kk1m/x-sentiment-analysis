# Data Directory

This directory contains runtime data, logs, and configuration files.

## Structure

```
data/
├── logs/
│   └── collection_log.csv      # Collection history and quota tracking
├── community_config.json        # Community search configuration
├── token_state.json            # X API token rotation state
└── samples/
    └── 10tweetsdata.yml        # Sample data for reference
```

## Files

### Logs
- **collection_log.csv** - Tracks all tweet collection attempts, successes, failures, and rate limits

### Configuration
- **community_config.json** - Stores the community ID for "Irresponsibly Long $MSTR"
- **token_state.json** - Manages X API token rotation and rate limit state

### Samples
- **10tweetsdata.yml** - Sample tweet data for reference/testing

## Git Ignore

The following files are gitignored as they contain runtime state:
- `token_state.json` - Runtime token state
- `logs/*.csv` - Log files

Configuration files like `community_config.json` are tracked in git.
