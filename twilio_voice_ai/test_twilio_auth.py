#!/usr/bin/env python3
"""
Direct Twilio API test to verify credentials and make a call
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

print("🔑 Testing Twilio Credentials")
print("=" * 50)
print(f"Account SID: {TWILIO_ACCOUNT_SID}")
print(f"Auth Token: {TWILIO_AUTH_TOKEN[:10]}..." if TWILIO_AUTH_TOKEN else "Auth Token: None")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    print("❌ Missing Twilio credentials in .env file")
    exit(1)

try:
    # Initialize Twilio client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Test connection by fetching account info
    print("\n📞 Testing Twilio Connection...")
    account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
    print(f"✅ Connection successful! Account status: {account.status}")
    
    # Make the call
    print("\n🚀 Making outbound call...")
    call = client.calls.create(
        to="+61425406759",      # Verified number
        from_="+18105055167",   # Your Twilio number
        url="http://demo.twilio.com/docs/voice.xml"  # Simple demo TwiML
    )
    
    print(f"✅ Call initiated successfully!")
    print(f"📋 Call SID: {call.sid}")
    print(f"📱 From: {call.from_formatted}")
    print(f"📱 To: {call.to}")
    print(f"📊 Status: {call.status}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 This could indicate:")
    print("   - Incorrect Auth Token")
    print("   - Account SID mismatch")
    print("   - Network connectivity issues")
    print("   - Trial account restrictions") 