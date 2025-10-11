#!/usr/bin/env python3
"""
View API Logs
CLI tool to view and analyze API call logs
"""
import sys
from datetime import datetime, timedelta
from backend.src.storage.database import get_session
from backend.src.models.api_log import APILog
from backend.src.services.api_logger import APILogger


def print_recent_logs(limit=10, service=None):
    """Print recent API logs"""
    logs = APILogger.get_recent_logs(limit=limit, service=service)
    
    if not logs:
        print("No API logs found")
        return
    
    print(f"\n📋 Recent API Logs (last {limit}):")
    print("=" * 100)
    
    for log in logs:
        status_emoji = "✅" if log.status == 'success' else "❌"
        
        print(f"\n{status_emoji} [{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log.service.upper()}")
        print(f"   Model: {log.model or 'N/A'}")
        print(f"   Status: {log.status}")
        
        if log.response_time_ms:
            print(f"   Latency: {log.response_time_ms}ms")
        
        if log.cost_usd:
            print(f"   Cost: ${log.cost_usd:.6f}")
        
        if log.tokens_used:
            print(f"   Tokens: {log.tokens_used}")
        
        if log.user_message:
            msg = log.user_message[:60] + "..." if len(log.user_message) > 60 else log.user_message
            print(f"   Message: {msg}")
        
        if log.error_message:
            print(f"   Error: {log.error_message}")
        
        if log.post_id:
            print(f"   Post ID: {log.post_id}")


def print_stats(hours=24):
    """Print API usage statistics"""
    stats = APILogger.get_stats(hours=hours)
    
    print(f"\n📊 API Usage Statistics (last {hours} hours):")
    print("=" * 100)
    print(f"   Total Calls: {stats['total_calls']}")
    print(f"   Successful: {stats['successful']} ({stats['success_rate']:.1f}%)")
    print(f"   Failed: {stats['failed']}")
    print(f"   Total Cost: ${stats['total_cost_usd']:.6f}")
    print(f"   Avg Latency: {stats['avg_latency_ms']:.0f}ms")


def print_expensive_calls(limit=5):
    """Print most expensive API calls"""
    session = get_session()
    
    try:
        logs = session.query(APILog).filter(
            APILog.cost_usd.isnot(None)
        ).order_by(
            APILog.cost_usd.desc()
        ).limit(limit).all()
        
        if not logs:
            print("\nNo cost data available")
            return
        
        print(f"\n💰 Most Expensive API Calls (top {limit}):")
        print("=" * 100)
        
        for i, log in enumerate(logs, 1):
            print(f"\n{i}. ${log.cost_usd:.6f} - {log.service} ({log.model})")
            print(f"   Time: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Tokens: {log.tokens_used}")
            if log.user_message:
                msg = log.user_message[:60] + "..." if len(log.user_message) > 60 else log.user_message
                print(f"   Message: {msg}")
    
    finally:
        session.close()


def print_failed_calls(limit=10):
    """Print failed API calls"""
    session = get_session()
    
    try:
        logs = session.query(APILog).filter(
            APILog.status == 'error'
        ).order_by(
            APILog.timestamp.desc()
        ).limit(limit).all()
        
        if not logs:
            print("\n✅ No failed API calls")
            return
        
        print(f"\n❌ Failed API Calls (last {limit}):")
        print("=" * 100)
        
        for log in logs:
            print(f"\n[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log.service}")
            print(f"   Error: {log.error_message}")
            if log.user_message:
                msg = log.user_message[:60] + "..." if len(log.user_message) > 60 else log.user_message
                print(f"   Message: {msg}")
    
    finally:
        session.close()


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python view_api_logs.py recent [limit]     - Show recent logs")
        print("  python view_api_logs.py stats [hours]      - Show usage statistics")
        print("  python view_api_logs.py expensive [limit]  - Show expensive calls")
        print("  python view_api_logs.py failed [limit]     - Show failed calls")
        return
    
    command = sys.argv[1]
    
    if command == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print_recent_logs(limit=limit)
    
    elif command == "stats":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        print_stats(hours=hours)
    
    elif command == "expensive":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        print_expensive_calls(limit=limit)
    
    elif command == "failed":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print_failed_calls(limit=limit)
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
