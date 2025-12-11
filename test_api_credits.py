#!/usr/bin/env python3
"""
Quick test to check OpenRouter API credits and connectivity.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ No API key found in .env file")
    exit(1)

print(f"✅ API key found: {api_key[:20]}...")

# Test API call
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "anthropic/claude-3.5-sonnet",
    "messages": [{"role": "user", "content": "Say 'hello' in one word"}],
    "max_tokens": 10
}

print("\n🔍 Testing API connection...")
try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ API is working!")
        print(f"💬 Response: {result['choices'][0]['message']['content']}")
        print(f"\n✨ Your OpenRouter API is ready to use!")
    elif response.status_code == 402:
        print(f"❌ Insufficient credits")
        print(f"💳 Please add credits at: https://openrouter.ai/credits")
        print(f"\nResponse: {response.text}")
    elif response.status_code == 401:
        print(f"❌ Invalid API key")
        print(f"🔑 Check your API key at: https://openrouter.ai/keys")
    elif response.status_code == 429:
        print(f"⏰ Rate limit exceeded")
        print(f"Please wait a moment and try again")
    else:
        print(f"❌ Unexpected error")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
