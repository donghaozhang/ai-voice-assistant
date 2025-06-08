#!/usr/bin/env python3
"""
Test the make-call endpoint
"""

import requests
import json

# Test the make-call endpoint
url = "http://localhost:5050/make-call"
payload = {
    "to": "+61425406759",  # Your verified number
    "from": "+18105551234"  # Placeholder Twilio number
}

headers = {
    "Content-Type": "application/json"
}

print("📞 Testing Make-Call Endpoint")
print("=" * 40)
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📄 Response Body: {response.text}")
    
    if response.status_code == 200:
        print("✅ Make-call endpoint working!")
    else:
        print("❌ Make-call endpoint failed")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server. Is it running on port 5050?")
except Exception as e:
    print(f"❌ Error: {e}")

# Also test the root endpoint
print("\n🏠 Testing Root Endpoint")
try:
    root_response = requests.get("http://localhost:5050/")
    print(f"Root endpoint: {root_response.text}")
except Exception as e:
    print(f"Root endpoint error: {e}")
    
# Test API documentation endpoint
print("\n📚 Testing API Docs")
try:
    docs_response = requests.get("http://localhost:5050/docs")
    print(f"API docs status: {docs_response.status_code}")
except Exception as e:
    print(f"API docs error: {e}") 