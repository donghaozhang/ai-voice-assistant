#!/usr/bin/env python3
"""
OpenAI Realtime API WebSocket Client

This module provides a Python client for connecting to OpenAI's Realtime API
via WebSockets for real-time speech-to-speech conversations and transcription.

Features:
- WebSocket connection management
- Real-time audio streaming
- Speech-to-speech conversations
- Transcription-only mode
- Event handling and session management
- Error handling and reconnection
"""

import os
import json
import asyncio
import base64
import threading
import pyaudio
import wave
import tempfile
from typing import Optional, Callable, Dict, Any, List
import websocket
from datetime import datetime


class OpenAIRealtimeClient:
    """
    OpenAI Realtime API WebSocket Client
    
    Supports both speech-to-speech conversations and transcription-only mode.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-realtime-preview-2024-12-17",
        intent: str = "speech_to_speech",  # or "transcription"
        voice: str = "verse",
        temperature: float = 0.7,
        auto_connect: bool = True
    ):
        """
        Initialize the Realtime API client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use for the session
            intent: 'speech_to_speech' or 'transcription'
            voice: Voice to use for speech synthesis
            temperature: Temperature for response generation
            auto_connect: Whether to auto-connect on initialization
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        self.model = model
        self.intent = intent
        self.voice = voice
        self.temperature = temperature
        
        # WebSocket connection
        self.ws = None
        self.connected = False
        self.session_id = None
        
        # Audio configuration
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 24000
        self.chunk_size = 1024
        
        # Audio streams
        self.audio_input = None
        self.audio_output = None
        self.recording = False
        self.playing = False
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Session configuration
        self.session_config = {
            "voice": self.voice,
            "temperature": self.temperature,
            "instructions": "You are a helpful AI assistant.",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500
            }
        }
        
        if auto_connect:
            asyncio.create_task(self.connect())
    
    def on(self, event_type: str, handler: Callable):
        """Register an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def emit(self, event_type: str, data: Any = None):
        """Emit an event to all registered handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Error in event handler for {event_type}: {e}")
    
    async def connect(self):
        """Connect to the OpenAI Realtime API."""
        try:
            # Build WebSocket URL
            base_url = "wss://api.openai.com/v1/realtime"
            if self.intent == "transcription":
                url = f"{base_url}?intent=transcription"
            else:
                url = f"{base_url}?model={self.model}"
            
            # Headers
            headers = [
                f"Authorization: Bearer {self.api_key}",
                "OpenAI-Beta: realtime=v1"
            ]
            
            # Create WebSocket connection
            self.ws = websocket.WebSocketApp(
                url,
                header=headers,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start WebSocket in a separate thread
            ws_thread = threading.Thread(target=self.ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Wait for connection
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            raise
    
    def _on_open(self, ws):
        """Handle WebSocket connection opened."""
        print("Connected to OpenAI Realtime API")
        self.connected = True
        self.emit("connected")
        
        # Send session configuration for speech-to-speech
        if self.intent != "transcription":
            self.send_event("session.update", {"session": self.session_config})
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages."""
        try:
            event = json.loads(message)
            event_type = event.get("type")
            
            # Handle different event types
            if event_type == "session.created":
                self.session_id = event.get("session", {}).get("id")
                self.emit("session_created", event)
                
            elif event_type == "conversation.item.input_audio_transcription.completed":
                transcript = event.get("transcript", "")
                self.emit("transcription", {"text": transcript})
                
            elif event_type == "response.audio.delta":
                audio_data = event.get("delta", "")
                if audio_data:
                    self._play_audio_chunk(base64.b64decode(audio_data))
                    
            elif event_type == "response.output_item.added":
                self.emit("response_started", event)
                
            elif event_type == "response.done":
                self.emit("response_completed", event)
                
            elif event_type == "conversation.item.created":
                self.emit("conversation_item", event)
                
            elif event_type == "error":
                error_msg = event.get("error", {}).get("message", "Unknown error")
                print(f"API Error: {error_msg}")
                self.emit("error", event)
            
            # Emit generic event
            self.emit("event", event)
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse message: {e}")
        except Exception as e:
            print(f"Error handling message: {e}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors."""
        print(f"WebSocket error: {error}")
        self.emit("error", {"error": str(error)})
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closed."""
        print("WebSocket connection closed")
        self.connected = False
        self.emit("disconnected")
    
    def send_event(self, event_type: str, data: Dict[str, Any] = None):
        """Send an event to the API."""
        if not self.connected or not self.ws:
            print("Not connected to API")
            return
            
        event = {"type": event_type}
        if data:
            event.update(data)
            
        try:
            self.ws.send(json.dumps(event))
        except Exception as e:
            print(f"Failed to send event: {e}")
    
    def start_recording(self):
        """Start recording audio from microphone."""
        if self.recording:
            return
            
        try:
            p = pyaudio.PyAudio()
            self.audio_input = p.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.recording = True
            
            # Start recording in a separate thread
            recording_thread = threading.Thread(target=self._record_audio)
            recording_thread.daemon = True
            recording_thread.start()
            
            print("Started recording...")
            self.emit("recording_started")
            
        except Exception as e:
            print(f"Failed to start recording: {e}")
    
    def stop_recording(self):
        """Stop recording audio."""
        if not self.recording:
            return
            
        self.recording = False
        
        if self.audio_input:
            self.audio_input.stop_stream()
            self.audio_input.close()
            self.audio_input = None
            
        print("Stopped recording")
        self.emit("recording_stopped")
    
    def _record_audio(self):
        """Record audio and send to API."""
        while self.recording and self.audio_input:
            try:
                data = self.audio_input.read(self.chunk_size, exception_on_overflow=False)
                
                # Encode audio data as base64
                audio_b64 = base64.b64encode(data).decode()
                
                # Send audio to API
                self.send_event("input_audio_buffer.append", {
                    "audio": audio_b64
                })
                
            except Exception as e:
                print(f"Error recording audio: {e}")
                break
    
    def _play_audio_chunk(self, audio_data: bytes):
        """Play audio chunk from the API."""
        try:
            if not self.audio_output:
                p = pyaudio.PyAudio()
                self.audio_output = p.open(
                    format=self.audio_format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    output=True
                )
            
            self.audio_output.write(audio_data)
            
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def send_text_message(self, text: str):
        """Send a text message to the assistant."""
        self.send_event("conversation.item.create", {
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text
                    }
                ]
            }
        })
        
        # Trigger response generation
        self.send_event("response.create")
    
    def commit_audio_buffer(self):
        """Commit the current audio buffer and trigger processing."""
        self.send_event("input_audio_buffer.commit")
    
    def create_response(self):
        """Trigger response generation."""
        self.send_event("response.create")
    
    def cancel_response(self):
        """Cancel the current response generation."""
        self.send_event("response.cancel")
    
    def update_session(self, config: Dict[str, Any]):
        """Update session configuration."""
        self.session_config.update(config)
        self.send_event("session.update", {"session": self.session_config})
    
    def disconnect(self):
        """Disconnect from the API."""
        self.recording = False
        self.connected = False
        
        if self.audio_input:
            self.audio_input.close()
            
        if self.audio_output:
            self.audio_output.close()
            
        if self.ws:
            self.ws.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class RealtimeTranscriber(OpenAIRealtimeClient):
    """
    Specialized client for transcription-only use cases.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        kwargs["intent"] = "transcription"
        super().__init__(api_key=api_key, **kwargs)
        
        # Store transcriptions
        self.transcriptions: List[Dict[str, Any]] = []
        
        # Register transcription handler
        self.on("transcription", self._handle_transcription)
    
    def _handle_transcription(self, data):
        """Handle transcription events."""
        transcript = {
            "text": data.get("text", ""),
            "timestamp": datetime.now().isoformat()
        }
        self.transcriptions.append(transcript)
        print(f"Transcribed: {transcript['text']}")
    
    def get_transcriptions(self) -> List[Dict[str, Any]]:
        """Get all transcriptions."""
        return self.transcriptions.copy()
    
    def clear_transcriptions(self):
        """Clear stored transcriptions."""
        self.transcriptions.clear()


class RealtimeConversation(OpenAIRealtimeClient):
    """
    Specialized client for speech-to-speech conversations.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        kwargs["intent"] = "speech_to_speech"
        super().__init__(api_key=api_key, **kwargs)
        
        # Conversation state
        self.conversation_active = False
        
        # Register event handlers
        self.on("response_started", self._handle_response_started)
        self.on("response_completed", self._handle_response_completed)
    
    def _handle_response_started(self, data):
        """Handle response generation started."""
        print("Assistant is responding...")
        self.conversation_active = True
    
    def _handle_response_completed(self, data):
        """Handle response generation completed."""
        print("Assistant finished responding")
        self.conversation_active = False
    
    def start_conversation(self):
        """Start a voice conversation."""
        print("Starting conversation. Press and hold to speak...")
        self.start_recording()
    
    def speak(self, duration: Optional[float] = None):
        """
        Speak for a specified duration or until stopped.
        
        Args:
            duration: Recording duration in seconds (None for manual stop)
        """
        self.start_recording()
        
        if duration:
            threading.Timer(duration, self.stop_speaking).start()
    
    def stop_speaking(self):
        """Stop speaking and process the audio."""
        self.stop_recording()
        self.commit_audio_buffer()
        self.create_response()
    
    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        return self.recording
    
    def is_responding(self) -> bool:
        """Check if assistant is currently responding."""
        return self.conversation_active 