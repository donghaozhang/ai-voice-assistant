#!/usr/bin/env python3
"""
Test Twilio API Key Authentication
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables (look in parent directory)
load_dotenv('../.env')

# Get credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_API_KEY_SID = os.getenv('TWILIO_API_KEY_SID')
TWILIO_API_KEY_SECRET = os.getenv('TWILIO_API_KEY_SECRET')

print("🔑 Testing Twilio API Key Authentication")
print("=" * 50)
print(f"Account SID: {TWILIO_ACCOUNT_SID}")
print(f"API Key SID: {TWILIO_API_KEY_SID}")
print(f"API Key Secret: {TWILIO_API_KEY_SECRET[:10]}..." if TWILIO_API_KEY_SECRET else "None")

if not all([TWILIO_ACCOUNT_SID, TWILIO_API_KEY_SID, TWILIO_API_KEY_SECRET]):
    print("❌ Missing required credentials!")
    exit(1)

try:
    # Initialize client with API Key
    client = Client(TWILIO_API_KEY_SID, TWILIO_API_KEY_SECRET, TWILIO_ACCOUNT_SID)
    
    # Test by fetching account info
    account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
    
    print("✅ API Key authentication successful!")
    print(f"Account Status: {account.status}")
    print(f"Account Type: {account.type}")
    print(f"Account Friendly Name: {account.friendly_name}")
    
    # Test listing phone numbers (if any)
    try:
        phone_numbers = client.incoming_phone_numbers.list(limit=5)
        print(f"Phone Numbers Available: {len(phone_numbers)}")
        for number in phone_numbers:
            print(f"  📞 {number.phone_number} ({number.friendly_name})")
    except Exception as e:
        print(f"Note: Could not list phone numbers: {e}")
    
except Exception as e:
    print(f"❌ API Key authentication failed: {e}")
    print("\n💡 Check that:")
    print("   - API Key SID starts with 'SK'")
    print("   - API Key Secret is correct")
    print("   - Account SID starts with 'AC'")
    print("   - API Key has the correct permissions") 