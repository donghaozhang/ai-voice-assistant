#!/usr/bin/env python3
"""
Test setup script for Twilio Voice AI Assistant
Verifies all dependencies are installed and basic configuration is correct.
"""

import sys
import os

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✓ Uvicorn {uvicorn.__version__}")
    except ImportError as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False
    
    try:
        import websockets
        print(f"✓ WebSockets {websockets.__version__}")
    except ImportError as e:
        print(f"✗ WebSockets import failed: {e}")
        return False
    
    try:
        import dotenv
        print(f"✓ python-dotenv")
    except ImportError as e:
        print(f"✗ python-dotenv import failed: {e}")
        return False
    
    try:
        import twilio
        print(f"✓ Twilio {twilio.__version__}")
    except ImportError as e:
        print(f"✗ Twilio import failed: {e}")
        return False
    
    print("All imports successful!")
    return True

def test_environment():
    """Test environment configuration."""
    print("\nTesting environment configuration...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✓ .env file exists")
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check for required environment variables
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != 'your_openai_api_key_here':
            print("✓ OPENAI_API_KEY is set")
        else:
            print("⚠ OPENAI_API_KEY not set or using placeholder value")
        
        port = os.getenv('PORT', '5050')
        print(f"✓ PORT set to {port}")
        
    else:
        print("⚠ .env file not found. Copy .env.example to .env and configure your API keys.")
    
    return True

def test_server_config():
    """Test server configuration without starting it."""
    print("\nTesting server configuration...")
    
    try:
        # Import the main module to check for syntax errors
        import main
        print("✓ main.py imports successfully")
        print("✓ FastAPI app configuration looks good")
        return True
    except Exception as e:
        print(f"✗ Error importing main.py: {e}")
        return False

def main():
    """Run all tests."""
    print("Twilio Voice AI Assistant - Setup Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test imports
    if test_imports():
        tests_passed += 1
    
    # Test environment
    if test_environment():
        tests_passed += 1
    
    # Test server config
    if test_server_config():
        tests_passed += 1
    
    print(f"\nTest Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 Setup looks good! You're ready to run the server.")
        print("\nNext steps:")
        print("1. Configure your .env file with real API keys")
        print("2. Run: python main.py")
        print("3. In another terminal, run: ngrok http 5050")
        print("4. Configure your Twilio webhook URL")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 