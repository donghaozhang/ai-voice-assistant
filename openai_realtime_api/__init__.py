"""
OpenAI Realtime API Python Implementation

A comprehensive Python client for the OpenAI Realtime API supporting:
- Real-time speech-to-speech conversations
- Real-time transcription
- WebSocket and WebRTC connections
- Event-driven architecture
- Secure token management

Example usage:
    from openai_realtime_api import RealtimeConversation, RealtimeTranscriber
    
    # Speech-to-speech conversation
    client = RealtimeConversation(voice="verse")
    await client.connect()
    client.start_conversation()
    
    # Real-time transcription
    transcriber = RealtimeTranscriber()
    await transcriber.connect()
    transcriber.start_recording()
"""

__version__ = "1.0.0"
__author__ = "Voice Agent Project"
__license__ = "MIT"

# Import main classes for easy access
try:
    from .websocket_client.realtime_client import (
        OpenAIRealtimeClient,
        RealtimeConversation,
        RealtimeTranscriber
    )
    
    __all__ = [
        "OpenAIRealtimeClient",
        "RealtimeConversation", 
        "RealtimeTranscriber"
    ]
    
except ImportError:
    # Handle missing dependencies gracefully
    __all__ = []
    
    def _missing_dependency_error(*args, **kwargs):
        raise ImportError(
            "OpenAI Realtime API dependencies not installed. "
            "Run: pip install -r requirements.txt"
        )
    
    OpenAIRealtimeClient = _missing_dependency_error
    RealtimeConversation = _missing_dependency_error
    RealtimeTranscriber = _missing_dependency_error 