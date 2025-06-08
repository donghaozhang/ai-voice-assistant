# Twilio Voice AI Assistant

A real-time voice AI assistant powered by Twilio Voice, Media Streams, and OpenAI's Realtime API. This project enables natural voice conversations with an AI assistant over the phone.

## Features

- **Real-time voice conversations** - Low-latency, bidirectional audio streaming
- **OpenAI Realtime API integration** - Powered by GPT-4o with real-time capabilities  
- **Twilio Voice integration** - Handle incoming phone calls with TwiML
- **WebSocket communication** - Real-time audio streaming between Twilio and OpenAI
- **Configurable AI personality** - Customizable system messages and voice settings

## Architecture

```
Phone Call → Twilio Voice → Media Streams → FastAPI Server → OpenAI Realtime API
                                            ↓
                                        WebSocket
                                        ↓
                                    Audio Processing
```

## Prerequisites

- **Python 3.8+**
- **OpenAI API key** with access to the Realtime API (currently in beta)
- **Twilio Account** with a voice-enabled phone number
- **ngrok** or similar tunneling service for local development

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
cd twilio_voice_ai
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Twilio Configuration  
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here

# Server Configuration
PORT=5050
```

### 3. Run the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 5050
```

### 4. Expose Your Local Server

Use ngrok to create a public URL for your local server:

```bash
ngrok http 5050
```

Copy the forwarding URL (e.g., `https://abc123.ngrok.app`)

### 5. Configure Twilio Webhook

1. Go to your [Twilio Console](https://console.twilio.com/)
2. Navigate to Phone Numbers → Manage → Active Numbers
3. Click on your voice-enabled phone number
4. In the **Voice & Fax** section, set **A CALL COMES IN** to:
   ```
   https://your-ngrok-url.ngrok.app/incoming-call
   ```
5. Save the configuration

### 6. Test Your Voice Assistant

Call your Twilio phone number and start talking to your AI assistant!

## Configuration Options

### AI Personality

Modify the `SYSTEM_MESSAGE` in `main.py` to customize the AI's personality:

```python
SYSTEM_MESSAGE = (
    "You are a helpful and bubbly AI assistant who loves to chat about "
    "anything the user is interested in and is prepared to offer them facts. "
    "You have a penchant for dad jokes, owl jokes, and rickrolling – subtly. "
    "Always stay positive, but work in a joke when appropriate."
)
```

### Voice Settings

Change the AI voice by modifying the `VOICE` variable:

```python
VOICE = 'alloy'  # Options: alloy, echo, fable, onyx, nova, shimmer
```

### Audio Settings

The application uses G.711 μ-law audio format for compatibility with Twilio:

- **Input format**: `g711_ulaw`
- **Output format**: `g711_ulaw`
- **Turn detection**: Server-side Voice Activity Detection (VAD)

## API Endpoints

- **GET /** - Health check endpoint
- **POST/GET /incoming-call** - Twilio webhook for incoming calls (returns TwiML)
- **WebSocket /media-stream** - Real-time audio streaming endpoint

## How It Works

### 1. Call Handling
When a call comes in, Twilio sends a webhook to `/incoming-call`, which returns TwiML instructions to:
- Play a welcome message
- Connect the call to a Media Stream WebSocket

### 2. Audio Streaming
The `/media-stream` WebSocket endpoint:
- Receives audio data from Twilio
- Forwards it to OpenAI's Realtime API
- Streams AI responses back to Twilio
- Handles connection state and error recovery

### 3. Real-time Processing
- **Twilio → OpenAI**: Audio chunks are base64 encoded and sent as `input_audio_buffer.append` events
- **OpenAI → Twilio**: AI responses come as `response.audio.delta` events and are forwarded to the caller

## Troubleshooting

### Common Issues

**"Missing the OpenAI API key" error**
- Ensure your `.env` file contains a valid `OPENAI_API_KEY`
- Verify you have access to the OpenAI Realtime API (currently in beta)

**Twilio webhook errors**
- Check that your ngrok URL is publicly accessible
- Verify the webhook URL in Twilio Console includes `/incoming-call`
- Ensure your server is running and accessible

**Audio quality issues**
- Check your internet connection stability
- Verify WebSocket connections are maintaining stable connections
- Monitor server logs for connection drops or errors

**No AI response**
- Check OpenAI API key permissions and quota
- Verify the WebSocket connection to OpenAI is established
- Look for error messages in server logs

### Debug Mode

Enable detailed logging by modifying `LOG_EVENT_TYPES` in `main.py`:

```python
LOG_EVENT_TYPES = [
    'response.content.done', 'rate_limits.updated', 'response.done',
    'input_audio_buffer.committed', 'input_audio_buffer.speech_stopped',
    'input_audio_buffer.speech_started', 'session.created',
    'session.updated', 'response.created', 'response.output_item.added'
]
```

## Limitations

- **Session Length**: OpenAI Realtime API sessions are limited to 15 minutes during beta
- **Audio Format**: Limited to G.711 μ-law for Twilio compatibility
- **Latency**: Depends on network conditions and server proximity

## Cost Considerations

- **OpenAI Realtime API**: Usage-based pricing for audio processing
- **Twilio Voice**: Per-minute charges for phone calls
- **Twilio Media Streams**: Additional charges for WebSocket audio streaming

## Security Notes

- Store API keys securely and never commit them to version control
- Use environment variables for all sensitive configuration
- Consider implementing authentication for production deployments
- Monitor API usage and set appropriate rate limits

## Resources

- [Twilio Voice Documentation](https://www.twilio.com/docs/voice)
- [OpenAI Realtime API Documentation](https://platform.openai.com/docs/guides/realtime)
- [Original Tutorial](https://www.twilio.com/en-us/blog/voice-ai-assistant-openai-realtime-api-python)

## License

This project is open source and available under the MIT License. 