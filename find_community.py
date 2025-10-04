"""
Find Community Script
Searches for "Irresponsibly Long $MSTR" community and saves the ID
Run this ONCE to get the community ID
"""
import asyncio
import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()


async def find_community():
    """Search for the community and save its ID"""
    
    print("🔍 Searching for 'Irresponsibly Long $MSTR' community...")
    print("")
    
    bearer_token = os.getenv("X_API_KEY")
    if not bearer_token:
        print("❌ Error: X_API_KEY not found in .env file")
        return
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    # Search for community
    search_queries = [
        "Irresponsibly Long MSTR",
        "Irresponsibly Long $MSTR",
        "Irresponsibly Long MicroStrategy"
    ]
    
    async with httpx.AsyncClient() as client:
        for query in search_queries:
            print(f"Trying: '{query}'")
            
            try:
                response = await client.get(
                    "https://api.twitter.com/2/communities/search",
                    headers=headers,
                    params={"query": query},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    communities = data.get("data", [])
                    
                    if communities:
                        print(f"✓ Found {len(communities)} communities")
                        print("")
                        
                        for i, community in enumerate(communities, 1):
                            print(f"{i}. {community.get('name')}")
                            print(f"   ID: {community.get('id')}")
                            print(f"   Description: {community.get('description', 'N/A')[:100]}")
                            print("")
                        
                        # Save the first match
                        if communities:
                            community_id = communities[0]["id"]
                            community_name = communities[0]["name"]
                            
                            config = {
                                "community_id": community_id,
                                "community_name": community_name,
                                "search_query": query,
                                "found_at": datetime.now().isoformat()
                            }
                            
                            with open("community_config.json", "w") as f:
                                json.dump(config, f, indent=2)
                            
                            print("✅ Community ID saved to community_config.json")
                            print(f"   Community: {community_name}")
                            print(f"   ID: {community_id}")
                            print("")
                            print("📊 Next step:")
                            print("   python collect_community_posts.py")
                            
                            return community_id
                    else:
                        print(f"   No results for '{query}'")
                        print("")
                
                elif response.status_code == 429:
                    print("⚠️  Rate limit hit. Wait 15 minutes and try again.")
                    return
                
                else:
                    print(f"   API returned status {response.status_code}")
                    print("")
                    
            except Exception as e:
                print(f"   Error: {e}")
                print("")
    
    print("❌ Community not found with any search query")
    print("")
    print("Options:")
    print("1. Check if community name is spelled differently")
    print("2. Verify community is public (not private)")
    print("3. Try searching on X directly to confirm it exists")


if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(find_community())
