import requests
import json

def make_call(to_number, from_number, server_url="http://localhost:5050"):
    """
    Make an outbound call using the Twilio Voice AI Assistant.
    
    Args:
        to_number: Phone number to call (e.g., "+1234567890")
        from_number: Your Twilio phone number (e.g., "+1987654321")
        server_url: URL of your running server
    """
    
    url = f"{server_url}/make-call"
    
    payload = {
        "to": to_number,
        "from": from_number
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if result.get("success"):
            print(f"✅ Call initiated successfully!")
            print(f"📞 Calling: {to_number}")
            print(f"📋 Call SID: {result.get('call_sid')}")
        else:
            print(f"❌ Failed to make call: {result.get('error')}")
            
        return result
        
    except Exception as e:
        print(f"❌ Error making call: {e}")
        return None

if __name__ == "__main__":
    # Example usage - REPLACE WITH REAL PHONE NUMBERS
    TO_NUMBER = "+61425406759"  # Verified phone number
    FROM_NUMBER = "+18105055167"  # Your actual Twilio phone number
    
    print("🤖 Twilio Voice AI Assistant - Outbound Call Demo")
    print("=" * 50)
    
    # Make the call
    result = make_call(TO_NUMBER, FROM_NUMBER)
    
    if result:
        print("\n📊 Response:")
        print(json.dumps(result, indent=2))
    
    print("\n💡 Note: Make sure to replace the phone numbers with real ones!")
    print("💡 Your server must be publicly accessible via ngrok for Twilio to reach it.") 