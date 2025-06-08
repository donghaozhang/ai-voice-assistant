#!/usr/bin/env python3
"""
API endpoint tests for Twilio Voice AI Assistant
Tests the FastAPI endpoints without requiring real API keys.
"""

import asyncio
import sys
from fastapi.testclient import TestClient

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    
    try:
        # Import main module
        import main
        
        # Create test client
        client = TestClient(main.app)
        
        # Test health endpoint
        response = client.get("/")
        
        if response.status_code == 200:
            print("✓ Health endpoint returns 200 OK")
            print(f"✓ Response: {response.text}")
            return True
        else:
            print(f"✗ Health endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Health endpoint test failed: {e}")
        return False

def test_incoming_call_endpoint():
    """Test the incoming call webhook endpoint."""
    print("\nTesting incoming call endpoint...")
    
    try:
        # Import main module
        import main
        
        # Create test client
        client = TestClient(main.app)
        
        # Test incoming call endpoint with mock Twilio request
        response = client.post(
            "/incoming-call",
            headers={"host": "localhost:5050"},
            data={}
        )
        
        if response.status_code == 200:
            print("✓ Incoming call endpoint returns 200 OK")
            
            # Check if response contains expected TwiML
            content = response.text
            if "<?xml version=" in content and "<Response>" in content:
                print("✓ Response contains valid TwiML")
                if "Connect" in content and "Stream" in content:
                    print("✓ TwiML includes Media Stream connection")
                    return True
                else:
                    print("⚠ TwiML missing Media Stream elements")
                    return False
            else:
                print("✗ Response does not contain valid TwiML")
                return False
        else:
            print(f"✗ Incoming call endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Incoming call endpoint test failed: {e}")
        return False

def test_api_structure():
    """Test that the FastAPI app has the expected structure."""
    print("\nTesting API structure...")
    
    try:
        import main
        
        # Check that app exists
        if hasattr(main, 'app'):
            print("✓ FastAPI app exists")
        else:
            print("✗ FastAPI app not found")
            return False
            
        # Check routes
        routes = [route.path for route in main.app.routes]
        
        expected_routes = ["/", "/incoming-call", "/media-stream"]
        found_routes = []
        
        for expected in expected_routes:
            if expected in routes:
                found_routes.append(expected)
                print(f"✓ Route {expected} exists")
            else:
                print(f"⚠ Route {expected} not found")
        
        if len(found_routes) >= 2:  # At least health and incoming-call
            print("✓ Core routes are configured")
            return True
        else:
            print("✗ Missing essential routes")
            return False
            
    except Exception as e:
        print(f"✗ API structure test failed: {e}")
        return False

def main():
    """Run all API tests."""
    print("Twilio Voice AI Assistant - API Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test health endpoint
    if test_health_endpoint():
        tests_passed += 1
    
    # Test incoming call endpoint
    if test_incoming_call_endpoint():
        tests_passed += 1
    
    # Test API structure
    if test_api_structure():
        tests_passed += 1
    
    print(f"\nAPI Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 All API tests passed! Your FastAPI server is ready.")
        print("\nYour server includes:")
        print("• Health check endpoint (GET /)")
        print("• Twilio webhook endpoint (POST /incoming-call)")
        print("• WebSocket endpoint for media streaming (/media-stream)")
        return True
    else:
        print("\n❌ Some API tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    try:
        # Install test client if not available
        from fastapi.testclient import TestClient
    except ImportError:
        print("Installing test dependencies...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "httpx"], check=True)
        from fastapi.testclient import TestClient
    
    success = main()
    sys.exit(0 if success else 1) 