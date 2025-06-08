#!/usr/bin/env python3
"""
Installation script for Twilio Voice AI Assistant
Automates the setup process including dependency installation and environment configuration.
"""

import subprocess
import sys
import os
import shutil

def run_command(command, description=""):
    """Run a shell command and return success status."""
    print(f"Running: {command}")
    if description:
        print(f"  {description}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("  ✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed: {e}")
        if e.stdout:
            print(f"  stdout: {e.stdout}")
        if e.stderr:
            print(f"  stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is supported")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} is not supported. Need Python 3.8+")
        return False

def check_pip():
    """Check if pip is available."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        print("✓ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("✗ pip is not available")
        return False

def install_dependencies():
    """Install Python dependencies from requirements.txt."""
    print("\nInstalling Python dependencies...")
    return run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                      "Installing FastAPI, Uvicorn, WebSockets, python-dotenv, and Twilio")

def setup_environment():
    """Set up the environment file."""
    print("\nSetting up environment configuration...")
    
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✓ Created .env file from .env.example")
            print("⚠ Please edit .env file and add your API keys!")
            return True
        else:
            print("✗ .env.example file not found")
            return False
    else:
        print("✓ .env file already exists")
        return True

def check_ngrok():
    """Check if ngrok is available."""
    print("\nChecking for ngrok...")
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ ngrok is available")
            print(f"  Version: {result.stdout.strip()}")
            return True
        else:
            print("⚠ ngrok not found in PATH")
            return False
    except FileNotFoundError:
        print("⚠ ngrok not found. You'll need to install it from https://ngrok.com/")
        return False

def main():
    """Run the installation process."""
    print("Twilio Voice AI Assistant - Installation")
    print("=" * 50)
    
    # Check prerequisites
    print("Checking prerequisites...")
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return False
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Failed to setup environment")
        return False
    
    # Check for ngrok (optional but recommended)
    ngrok_available = check_ngrok()
    
    # Run setup test
    print("\nRunning setup verification...")
    if run_command(f"{sys.executable} test_setup.py", "Verifying installation"):
        print("\n🎉 Installation completed successfully!")
        
        print("\nNext steps:")
        print("1. Edit .env file and add your API keys:")
        print("   - OPENAI_API_KEY (from https://platform.openai.com/api-keys)")
        print("   - TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN (from https://console.twilio.com/)")
        print("")
        print("2. Start the server:")
        print("   python main.py")
        print("")
        print("3. In another terminal, expose your server (if you have ngrok):")
        print("   ngrok http 5050")
        print("")
        print("4. Configure your Twilio phone number webhook:")
        print("   - Go to https://console.twilio.com/")
        print("   - Navigate to Phone Numbers → Manage → Active Numbers")
        print("   - Set webhook URL to: https://your-ngrok-url.ngrok.app/incoming-call")
        
        if not ngrok_available:
            print("\n⚠ ngrok was not found. You'll need to:")
            print("   - Install ngrok from https://ngrok.com/")
            print("   - Or use another tunneling service to expose your local server")
        
        return True
    else:
        print("\n❌ Installation verification failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 