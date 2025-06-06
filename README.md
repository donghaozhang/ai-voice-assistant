# Voice Agent

A voice-activated AI assistant that can record audio, transcribe speech, generate intelligent responses using CrewAI, and speak back using text-to-speech.

## Features

- 🎙️ **Voice Recording**: Records audio input from microphone
- 🗣️ **Speech Transcription**: Converts speech to text using OpenAI Whisper
- 🧠 **AI Response**: Generates contextual responses using CrewAI agents
- 💭 **Memory**: Remembers conversations using mem0 for personalized responses
- 🔊 **Text-to-Speech**: Speaks responses using ElevenLabs voice synthesis

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MEM0_API_KEY=your_mem0_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

### 3. Get API Keys

- **OpenAI**: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Mem0**: Sign up and get your API key from [Mem0 App](https://app.mem0.ai/)
- **ElevenLabs**: Get your API key from [ElevenLabs API Keys](https://elevenlabs.io/app/api-keys)

### 4. Run the Voice Agent

```bash
# Run the enhanced version with memory
python voice_agent_original.py

# Or run the basic version
python voice_agent.py
```

## Configuration

You can customize the behavior by editing the `.env` file:

```env
# Optional Configuration
USER_ID=voice_user              # Unique identifier for memory storage
RECORDING_DURATION=4            # Recording duration in seconds
VOICE_ID=pNInz6obpgDQGcFmaJgB   # ElevenLabs voice ID (Adam voice)
```

## Usage

1. Run the script
2. Speak when prompted (it records for 4 seconds by default)
3. The assistant will transcribe, process, and respond
4. Say "quit" or "exit" to stop

## Files

- `voice_agent_original.py` - Enhanced version with mem0 memory integration
- `voice_agent.py` - Basic version without memory
- `tests/` - Individual component tests
- `.env` - Your API keys (create from `.env.example`)
- `.env.example` - Template for environment variables

## Troubleshooting

1. **Audio Issues**: Make sure your microphone is working and accessible
2. **API Key Errors**: Verify all API keys are correctly set in `.env`
3. **Memory Errors**: Check your mem0 API key and account status
4. **TTS Errors**: Verify your ElevenLabs API key and voice ID

## Security Note

Never commit your `.env` file to version control. It's already included in `.gitignore` for safety.