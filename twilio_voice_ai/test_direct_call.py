# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set environment variables for your credentials
# Read more at http://twil.io/secure

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

print("📞 Making direct Twilio call...")
print(f"From: +18105055167")
print(f"To: +61425406759")
print(f"Account SID: {account_sid}")
print(f"Auth Token: {auth_token[:10]}...")

try:
    call = client.calls.create(
      url="http://demo.twilio.com/docs/voice.xml",
      to="+61425406759",
      from_="+18105055167"
    )

    print("✅ Call created successfully!")
    print(f"Call SID: {call.sid}")
    
except Exception as e:
    print(f"❌ Call failed: {e}")
    print("\n💡 This might indicate:")
    print("   - Authentication issue with the token")
    print("   - Phone number verification required")
    print("   - Trial account restrictions") 