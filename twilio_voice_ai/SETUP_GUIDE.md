# Quick Setup Guide

## 🚀 Quick Start (Automated)

Run the automated installation script:

```bash
python install.py
```

This will:
- Check Python version compatibility  
- Install all required dependencies
- Set up environment configuration
- Verify the installation

## 🔧 Manual Setup

If you prefer manual setup:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Test Setup
```bash
python test_setup.py
```

## 📋 Required API Keys

You'll need these API keys in your `.env` file:

1. **OpenAI API Key** 
   - Get from: https://platform.openai.com/api-keys
   - Requires access to Realtime API (currently in beta)

2. **Twilio Credentials**
   - Account SID and Auth Token from: https://console.twilio.com/
   - A voice-enabled phone number

## 🏃‍♂️ Running the Server

```bash
python main.py
```

The server will start on http://localhost:5050

## 🌐 Exposing Your Server

Use ngrok to make your local server publicly accessible:

```bash
ngrok http 5050
```

Copy the forwarding URL (e.g., `https://abc123.ngrok.app`)

## 📞 Configure Twilio Webhook

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Phone Numbers → Manage → Active Numbers**
3. Click your voice-enabled number
4. Set **A CALL COMES IN** webhook to:
   ```
   https://your-ngrok-url.ngrok.app/incoming-call
   ```
5. Save configuration

## ✅ Test Your Voice Assistant

Call your Twilio phone number and start talking!

## 🐛 Troubleshooting

If you encounter issues:

1. Run `python test_setup.py` to verify configuration
2. Check that all API keys are properly set in `.env`
3. Ensure ngrok is running and webhook URL is correct
4. Check server logs for error messages

For more detailed troubleshooting, see the full [README.md](README.md). 