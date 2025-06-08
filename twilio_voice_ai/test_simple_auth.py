#!/usr/bin/env python3
"""
Simple Twilio authentication test
"""

import requests
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Live credentials
LIVE_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
LIVE_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

print("🔍 Testing Twilio Authentication")
print("=" * 50)

def test_credentials(account_sid, auth_token, cred_type):
    print(f"\n🔑 Testing {cred_type} credentials...")
    print(f"Account SID: {account_sid}")
    print(f"Auth Token: {auth_token[:10]}...")
    
    # Create basic auth header
    auth_str = f"{account_sid}:{auth_token}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    
    # Test with simple GET request
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}.json"
    headers = {"Authorization": f"Basic {encoded_auth}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ {cred_type} authentication successful!")
            data = response.json()
            print(f"Account Status: {data.get('status')}")
            print(f"Account Type: {data.get('type')}")
            return True
        else:
            print(f"❌ {cred_type} authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {cred_type} error: {e}")
        return False

# Test both credential sets
if LIVE_ACCOUNT_SID and LIVE_AUTH_TOKEN:
    live_success = test_credentials(LIVE_ACCOUNT_SID, LIVE_AUTH_TOKEN, "LIVE")
else:
    print("❌ LIVE credentials not found in .env file. Skipping test.")
    print("   Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")

print("\n💡 If this fails, the Auth Token may need to be regenerated or there may be account restrictions.") 