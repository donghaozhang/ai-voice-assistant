#!/usr/bin/env python3
"""
Direct test with exact credentials from console
"""
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Exact credentials from your console
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
API_KEY_SID = os.getenv("TWILIO_API_KEY_SID")
API_KEY_SECRET = os.getenv("TWILIO_API_KEY_SECRET")

print("🔑 Testing Direct API Key Credentials")
print("=" * 50)
print(f"Account SID: {ACCOUNT_SID}")
print(f"API Key SID: {API_KEY_SID}")
print(f"API Key Secret: {API_KEY_SECRET[:10] if API_KEY_SECRET else 'None'}...")

if not all([ACCOUNT_SID, API_KEY_SID, API_KEY_SECRET]):
    print("❌ Missing one or more required environment variables:")
    print("   - TWILIO_ACCOUNT_SID")
    print("   - TWILIO_API_KEY_SID")
    print("   - TWILIO_API_KEY_SECRET")
    exit(1)

try:
    # Test API Key authentication
    client = Client(API_KEY_SID, API_KEY_SECRET, ACCOUNT_SID)
    
    # Try to fetch account info
    account = client.api.accounts(ACCOUNT_SID).fetch()
    
    print("✅ API Key authentication successful!")
    print(f"Account Status: {account.status}")
    print(f"Account Type: {account.type}")
    
except Exception as e:
    print(f"❌ API Key failed: {e}")
    print("\n💡 This could indicate:")
    print("   - Incorrect API Key, Secret, or Account SID")
    print("   - Network connectivity issues")
    print("   - Account permissions issue") 