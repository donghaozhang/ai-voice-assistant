# voice_agent_original.py

import os, wave, tempfile
import pyaudio
from openai import OpenAI
from crewai import Agent, Crew, Task, Process
from elevenlabs import ElevenLabs
from mem0 import MemoryClient
from dotenv import load_dotenv
import pygame

# Load environment variables from .env file
load_dotenv()

# Verify required API keys are loaded
required_keys = ["OPENAI_API_KEY", "MEM0_API_KEY", "ELEVENLABS_API_KEY"]
missing_keys = [key for key in required_keys if not os.getenv(key)]
if missing_keys:
    raise ValueError(f"Missing required API keys in .env file: {missing_keys}")

# Setup clients with API keys from environment
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tts_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
memg = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

# Initialize pygame mixer for audio playback
try:
    pygame.mixer.init()
except:
    print("⚠️ Warning: pygame mixer initialization failed. TTS may not work.")

# Configuration from environment variables with defaults
USER_ID = os.getenv("USER_ID", "voice_user")
RECORDING_DURATION = int(os.getenv("RECORDING_DURATION", 4))
VOICE_ID = os.getenv("VOICE_ID", "pNInz6obpgDQGcFmaJgB")

# Record voice to temp WAV file
def record_wav(filename, seconds=None):
    if seconds is None:
        seconds = RECORDING_DURATION
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True,
                     frames_per_buffer=1024)
    frames = [stream.read(1024) for _ in range(0, int(44100 / 1024 * seconds))]
    stream.stop_stream(); stream.close(); pa.terminate()
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100); wf.writeframes(b''.join(frames))

# Transcribe audio
def transcribe(file_path):
    with open(file_path, "rb") as f:
        return openai_client.audio.transcriptions.create(model="whisper-1", file=f).text

# Speak reply
def speak(text):
    try:
        # Generate audio using ElevenLabs
        audio = tts_client.text_to_speech.convert(text=text, voice_id=VOICE_ID)
        
        # Save audio to temporary file
        temp_audio_path = f"temp_tts_{os.getpid()}.mp3"
        with open(temp_audio_path, 'wb') as f:
            for chunk in audio:
                f.write(chunk)
        
        # Play audio using pygame
        pygame.mixer.music.load(temp_audio_path)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        # Clean up temp file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            
    except Exception as e:
        print(f"🔇 TTS Error: {e}")
        print("Continuing without speech...")

# Create agent with basic memory only (no mem0 integration to avoid conflicts)
agent = Agent(
    role="Voice Assistant", 
    goal="Help the user and remember things.",
    backstory="You are a helpful voice assistant that can remember conversations and provide personalized responses."
)

# Agent logic with improved memory management
def get_reply(prompt):
    # Get relevant memories first
    context = ""
    try:
        memories = memg.search(prompt, user_id=USER_ID)
        if memories:
            context = "\nRelevant memories:\n" + "\n".join([f"- {m['memory']}" for m in memories[:3]])
    except Exception as e:
        print(f"💭 Memory search warning: {e}")
    
    # Create enhanced prompt with context
    enhanced_prompt = f"{prompt}{context}"
    
    crew = Crew(
        agents=[agent],
        tasks=[Task(
            description=f"Respond to the user's question: {enhanced_prompt}", 
            expected_output="A helpful and conversational response to the user's question",
            agent=agent
        )],
        process=Process.sequential,
        memory=True,  # Basic CrewAI memory only
        verbose=False  # Reduce noise
    )
    result = crew.kickoff()
    
    # Add conversation to memory in proper format
    try:
        conversation = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": getattr(result, "raw", str(result))}
        ]
        memg.add(conversation, user_id=USER_ID)
        print("💭 Memory updated successfully")
    except Exception as e:
        print(f"💭 Memory addition warning: {e}")
    
    return getattr(result, "raw", str(result))

# Main loop
def run():
    print("🎙️ Speak to your AI assistant (say 'quit' to exit)")
    while True:
        # Create a temporary file in current directory
        temp_path = f"temp_audio_{os.getpid()}.wav"
        try:
            record_wav(temp_path)
            text = transcribe(temp_path).strip()
            print(f"🗣️ You said: {text}")
            if text.lower() in ["quit", "exit"]: break
            reply = get_reply(text)
            print(f"🤖 {reply}"); speak(reply)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    run()