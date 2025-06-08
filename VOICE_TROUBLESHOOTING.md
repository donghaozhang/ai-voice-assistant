# Voice Agent Troubleshooting Guide

## 🔊 "I can't hear the voice agent talking"

### Quick Fixes:

#### 1. **Test Your Audio System**
```bash
cd openai_realtime_api/examples
python audio_test.py
```
This will test both audio output and microphone input. If this fails, the issue is with your system audio configuration.

#### 2. **Check Audio Debug Output**
When you run the voice agent, look for these debug messages:
- `🔊 Audio output stream initialized` - Means audio setup worked
- `🎵 Playing audio chunk: X bytes` - Means audio data is being received and played

If you don't see these messages, the API isn't sending audio responses.

#### 3. **Verify API Response**
The voice agent should show:
- `🎤 Audio committed, requesting response...` - When you stop speaking
- `🤖 Assistant is responding...` - When API starts generating response
- `✅ Assistant finished responding` - When response is complete

### Common Issues:

#### **Issue 1: No Audio Output Stream**
**Symptoms**: No `🔊 Audio output stream initialized` message
**Solution**: 
```bash
# Check available audio devices
python -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxOutputChannels']>0]"
```

#### **Issue 2: Audio Format Mismatch**
**Symptoms**: `❌ Error playing audio` messages
**Solution**: The voice agent uses 24kHz PCM16 format. Make sure your audio drivers support this.

#### **Issue 3: No Audio Chunks Received**
**Symptoms**: No `🎵 Playing audio chunk` messages
**Causes**:
- API key issues
- No speech input detected
- Server-side voice detection not triggering response

**Debug Steps**:
1. Check your speech is being transcribed: Look for `🎤 You said: [your text]`
2. Verify response generation: Look for `🤖 Assistant is responding...`
3. Check WebSocket messages for `response.audio.delta` events

#### **Issue 4: Audio Buffering Problems**
**Symptoms**: Choppy or delayed audio
**Solution**: The system uses real-time streaming. If you have buffering issues:
- Close other audio applications
- Check system CPU usage
- Ensure stable internet connection

### Windows-Specific Issues:

#### **Windows Audio Permissions**
1. Right-click the speaker icon in system tray
2. Select "Open Sound settings"
3. Ensure correct playback device is selected
4. Check app volume in Volume Mixer

#### **PyAudio Installation Issues**
If you get PyAudio errors:
```bash
# Try reinstalling PyAudio
pip uninstall pyaudio
pip install pyaudio
```

### Testing Steps:

#### **Step 1: Basic Audio Test**
```bash
cd openai_realtime_api/examples
python audio_test.py
```
Should play a 440Hz tone and record microphone input.

#### **Step 2: Import Test**
```bash
python -c "from websocket_client.realtime_client import RealtimeConversation; print('✅ Imports OK')"
```

#### **Step 3: API Connection Test**
```bash
# Set your API key first
set OPENAI_API_KEY=your-api-key-here
python speech_to_speech_example.py
```
Look for "🔗 Connected to OpenAI Realtime API" message.

### Environment Checklist:

- ✅ `ai-researcher` conda environment activated
- ✅ All dependencies installed: `pip install -r requirements.txt`
- ✅ OPENAI_API_KEY environment variable set
- ✅ Microphone and speakers connected and working
- ✅ Windows audio permissions enabled

### Advanced Debugging:

#### **Enable Verbose Logging**
Add this to the beginning of `speech_to_speech_example.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### **Check WebSocket Messages**
Add this event handler to see all API messages:
```python
@self.client.on("event")
def on_any_event(data):
    print(f"📨 API Event: {data.get('type', 'unknown')}")
```

### Still Having Issues?

1. **Run the audio test**: `python audio_test.py`
2. **Check your API key**: Make sure it's valid and has Realtime API access
3. **Try a different audio device**: Use headphones instead of speakers
4. **Check system resources**: Close other applications using audio
5. **Restart the terminal**: Sometimes audio drivers need a fresh start

### Expected Behavior:

When working correctly, you should see this flow:
1. `🔗 Connected to OpenAI Realtime API`
2. `🆔 Session created: sess_XXXXXX`
3. `🔊 Audio output stream initialized`
4. *Hold SPACE and speak*
5. `🔴 Recording started - speak now!`
6. `🎤 You said: [your speech]`
7. *Release SPACE*
8. `⏹️ Recording stopped - processing...`
9. `🎤 Audio committed, requesting response...`
10. `🤖 Assistant is responding...`
11. `🎵 Playing audio chunk: XXX bytes` (multiple times)
12. `✅ Assistant finished responding`

If you see steps 1-9 but not 10-12, the issue is with audio output. If you don't see step 6, the issue is with speech recognition. 