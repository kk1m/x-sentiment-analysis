"""
Test Community Query
Tests different query syntaxes to find posts from community ID
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

COMMUNITY_ID = "1761182781692850326"

async def test_query(query_name, query):
    """Test a specific query syntax"""
    print(f"\n{'='*60}")
    print(f"Testing: {query_name}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    bearer_token = os.getenv("X_API_KEY")
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "query": query,
        "max_results": 5,
        "tweet.fields": "created_at,author_id,public_metrics,lang",
        "expansions": "author_id",
        "user.fields": "username,name,verified,public_metrics"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=30.0
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", [])
                print(f"✅ SUCCESS! Found {len(posts)} posts")
                
                if posts:
                    print("\nSample post:")
                    post = posts[0]
                    print(f"  Text: {post['text'][:100]}...")
                    print(f"  Likes: {post.get('public_metrics', {}).get('like_count', 0)}")
                return True
                
            elif response.status_code == 400:
                error = response.json()
                print(f"❌ BAD REQUEST - Invalid query syntax")
                print(f"   Error: {error}")
                return False
                
            elif response.status_code == 429:
                print(f"⚠️  RATE LIMIT - Query syntax might be valid, but can't test now")
                return None
                
            else:
                print(f"❌ Error {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False


async def main():
    """Test various query syntaxes"""
    
    print("🧪 Testing Community Query Syntaxes")
    print(f"Community ID: {COMMUNITY_ID}")
    
    queries = [
        ("context: operator", f"context:{COMMUNITY_ID}"),
        ("context: with space", f"context: {COMMUNITY_ID}"),
        ("conversation_id", f"conversation_id:{COMMUNITY_ID}"),
        ("community: operator", f"community:{COMMUNITY_ID}"),
        ("from community", f"from_community:{COMMUNITY_ID}"),
        ("in: operator", f"in:{COMMUNITY_ID}"),
        ("url: operator", f"url:communities/{COMMUNITY_ID}"),
    ]
    
    results = {}
    
    for name, query in queries:
        result = await test_query(name, query)
        results[name] = result
        
        # If we hit rate limit, stop testing
        if result is None:
            print("\n⚠️  Rate limit hit. Can't test remaining queries.")
            break
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, result in results.items():
        if result is True:
            print(f"✅ {name}: WORKS")
        elif result is False:
            print(f"❌ {name}: FAILED")
        elif result is None:
            print(f"⚠️  {name}: RATE LIMITED (unknown)")
    
    print("\nNote: If all queries fail with 400, the community query")
    print("feature might not be available on free tier.")


if __name__ == "__main__":
    asyncio.run(main())
