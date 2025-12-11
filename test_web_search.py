"""
Quick test to verify web search functionality
"""

import requests
from urllib.parse import quote

def test_web_search():
    """Test DuckDuckGo web search."""
    query = "Hong-Ou-Mandel effect quantum optics"
    
    print(f"🔍 Testing web search for: {query}")
    print("-" * 70)
    
    try:
        encoded_query = quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1"
        
        print(f"URL: {url}\n")
        
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            
            # Extract abstract if available
            if data.get('Abstract'):
                print("\n📄 Abstract Found:")
                print(f"  Title: {data.get('Heading', 'N/A')}")
                print(f"  Abstract: {data.get('Abstract', 'N/A')[:200]}...")
                print(f"  URL: {data.get('AbstractURL', 'N/A')}")
                
                results.append({
                    'title': data.get('Heading', 'DuckDuckGo Result'),
                    'description': data.get('Abstract', ''),
                    'url': data.get('AbstractURL', '')
                })
            
            # Add related topics
            print(f"\n📚 Related Topics: {len(data.get('RelatedTopics', []))} found")
            for i, topic in enumerate(data.get('RelatedTopics', [])[:3], 1):
                if isinstance(topic, dict) and 'Text' in topic:
                    print(f"\n  {i}. {topic.get('Text', '')[:100]}...")
                    print(f"     URL: {topic.get('FirstURL', 'N/A')}")
                    
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        'description': topic.get('Text', ''),
                        'url': topic.get('FirstURL', '')
                    })
            
            print(f"\n✅ Total results collected: {len(results)}")
            return {"results": results}
        
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            return {"results": []}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"results": []}

if __name__ == "__main__":
    result = test_web_search()
    
    print("\n" + "="*70)
    print("FINAL RESULT:")
    print("="*70)
    print(f"Found {len(result.get('results', []))} results")
    for i, r in enumerate(result.get('results', []), 1):
        print(f"\n{i}. {r.get('title', 'Untitled')}")
        print(f"   {r.get('description', '')[:150]}...")
