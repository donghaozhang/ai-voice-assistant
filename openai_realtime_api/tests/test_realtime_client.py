#!/usr/bin/env python3
"""
Unit tests for OpenAI Realtime API client implementation.
"""

import unittest
import asyncio
import os
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from websocket_client.realtime_client import (
    OpenAIRealtimeClient,
    RealtimeConversation,
    RealtimeTranscriber
)


class TestOpenAIRealtimeClient(unittest.TestCase):
    """Test cases for OpenAIRealtimeClient."""
    
    def setUp(self):
        """Set up test environment."""
        self.api_key = "test-api-key"
        
    def test_client_initialization(self):
        """Test client initialization."""
        client = OpenAIRealtimeClient(
            api_key=self.api_key,
            auto_connect=False
        )
        
        self.assertEqual(client.api_key, self.api_key)
        self.assertEqual(client.model, "gpt-4o-realtime-preview-2024-12-17")
        self.assertEqual(client.voice, "verse")
        self.assertFalse(client.connected)
        
    def test_client_initialization_without_api_key(self):
        """Test client initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                OpenAIRealtimeClient(auto_connect=False)
    
    def test_event_handler_registration(self):
        """Test event handler registration."""
        client = OpenAIRealtimeClient(
            api_key=self.api_key,
            auto_connect=False
        )
        
        handler = Mock()
        client.on("test_event", handler)
        
        self.assertIn("test_event", client.event_handlers)
        self.assertIn(handler, client.event_handlers["test_event"])
    
    def test_event_emission(self):
        """Test event emission."""
        client = OpenAIRealtimeClient(
            api_key=self.api_key,
            auto_connect=False
        )
        
        handler = Mock()
        client.on("test_event", handler)
        
        test_data = {"message": "test"}
        client.emit("test_event", test_data)
        
        handler.assert_called_once_with(test_data)
    
    def test_session_config(self):
        """Test session configuration."""
        client = OpenAIRealtimeClient(
            api_key=self.api_key,
            voice="nova",
            temperature=0.5,
            auto_connect=False
        )
        
        self.assertEqual(client.session_config["voice"], "nova")
        self.assertEqual(client.session_config["temperature"], 0.5)
        self.assertEqual(client.session_config["input_audio_format"], "pcm16")
    
    @patch('websocket.WebSocketApp')
    async def test_connect(self, mock_websocket):
        """Test WebSocket connection."""
        client = OpenAIRealtimeClient(
            api_key=self.api_key,
            auto_connect=False
        )
        
        mock_ws = Mock()
        mock_websocket.return_value = mock_ws
        
        await client.connect()
        
        mock_websocket.assert_called_once()
        self.assertIsNotNone(client.ws)
    
    def test_send_event_not_connected(self):
        """Test sending event when not connected."""
        client = OpenAIRealtimeClient(
            api_key=self.api_key,
            auto_connect=False
        )
        
        # Should not raise exception, just print message
        client.send_event("test.event", {"data": "test"})
        
        # Verify no WebSocket was created
        self.assertIsNone(client.ws)


class TestRealtimeConversation(unittest.TestCase):
    """Test cases for RealtimeConversation."""
    
    def setUp(self):
        """Set up test environment."""
        self.api_key = "test-api-key"
    
    def test_conversation_initialization(self):
        """Test conversation client initialization."""
        client = RealtimeConversation(
            api_key=self.api_key,
            auto_connect=False
        )
        
        self.assertEqual(client.intent, "speech_to_speech")
        self.assertFalse(client.conversation_active)
    
    def test_speaking_state(self):
        """Test speaking state tracking."""
        client = RealtimeConversation(
            api_key=self.api_key,
            auto_connect=False
        )
        
        self.assertFalse(client.is_speaking())
        self.assertFalse(client.is_responding())
    
    @patch('pyaudio.PyAudio')
    def test_start_conversation(self, mock_pyaudio):
        """Test starting conversation."""
        mock_audio = Mock()
        mock_pyaudio.return_value = mock_audio
        mock_audio.open.return_value = Mock()
        
        client = RealtimeConversation(
            api_key=self.api_key,
            auto_connect=False
        )
        
        # Mock the start_recording method
        with patch.object(client, 'start_recording') as mock_start:
            client.start_conversation()
            mock_start.assert_called_once()


class TestRealtimeTranscriber(unittest.TestCase):
    """Test cases for RealtimeTranscriber."""
    
    def setUp(self):
        """Set up test environment."""
        self.api_key = "test-api-key"
    
    def test_transcriber_initialization(self):
        """Test transcriber initialization."""
        transcriber = RealtimeTranscriber(
            api_key=self.api_key,
            auto_connect=False
        )
        
        self.assertEqual(transcriber.intent, "transcription")
        self.assertEqual(len(transcriber.transcriptions), 0)
    
    def test_transcription_handling(self):
        """Test transcription event handling."""
        transcriber = RealtimeTranscriber(
            api_key=self.api_key,
            auto_connect=False
        )
        
        # Simulate transcription event
        test_data = {"text": "Hello world"}
        transcriber._handle_transcription(test_data)
        
        self.assertEqual(len(transcriber.transcriptions), 1)
        self.assertEqual(transcriber.transcriptions[0]["text"], "Hello world")
    
    def test_clear_transcriptions(self):
        """Test clearing transcriptions."""
        transcriber = RealtimeTranscriber(
            api_key=self.api_key,
            auto_connect=False
        )
        
        # Add some transcriptions
        transcriber.transcriptions.append({"text": "test", "timestamp": "now"})
        self.assertEqual(len(transcriber.transcriptions), 1)
        
        # Clear transcriptions
        transcriber.clear_transcriptions()
        self.assertEqual(len(transcriber.transcriptions), 0)
    
    def test_get_transcriptions(self):
        """Test getting transcriptions."""
        transcriber = RealtimeTranscriber(
            api_key=self.api_key,
            auto_connect=False
        )
        
        # Add test transcription
        test_transcript = {"text": "test", "timestamp": "now"}
        transcriber.transcriptions.append(test_transcript)
        
        # Get transcriptions (should return copy)
        result = transcriber.get_transcriptions()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], test_transcript)
        
        # Verify it's a copy (modifying result shouldn't affect original)
        result.clear()
        self.assertEqual(len(transcriber.transcriptions), 1)


class TestWebSocketIntegration(unittest.TestCase):
    """Integration tests for WebSocket functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.api_key = "test-api-key"
    
    @patch('websocket.WebSocketApp')
    def test_websocket_message_handling(self, mock_websocket):
        """Test WebSocket message handling."""
        client = OpenAIRealtimeClient(
            api_key=self.api_key,
            auto_connect=False
        )
        
        # Mock WebSocket
        mock_ws = Mock()
        mock_websocket.return_value = mock_ws
        client.ws = mock_ws
        
        # Test session.created event
        session_event = {
            "type": "session.created",
            "session": {"id": "test-session-123"}
        }
        
        client._on_message(mock_ws, json.dumps(session_event))
        self.assertEqual(client.session_id, "test-session-123")
    
    def test_error_handling(self):
        """Test error handling in message processing."""
        client = OpenAIRealtimeClient(
            api_key=self.api_key,
            auto_connect=False
        )
        
        mock_ws = Mock()
        
        # Test invalid JSON
        client._on_message(mock_ws, "invalid json")
        
        # Should not raise exception, just log error
        # In a real test, you'd capture the log output


if __name__ == "__main__":
    # Import json for the tests
    import json
    
    unittest.main() 