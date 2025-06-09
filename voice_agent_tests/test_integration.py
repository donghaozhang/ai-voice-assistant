import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIntegration(unittest.TestCase):
    """Integration tests that test multiple components working together."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.temp_audio_file.write(b'fake_audio_data')
        self.temp_audio_file.close()
        
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.temp_audio_file.name):
            os.remove(self.temp_audio_file.name)
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    @patch('voice_agent_original.openai_client')
    @patch('voice_agent_original.pyaudio.PyAudio')
    def test_full_conversation_flow(self, mock_pyaudio, mock_openai_client, mock_crew_class,
                                   mock_memg, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test the complete flow from recording to response."""
        from voice_agent_original import record_wav, transcribe, get_reply, speak
        
        # Mock recording
        mock_pa = MagicMock()
        mock_stream = MagicMock()
        mock_stream.read.return_value = b'\x00' * 1024
        mock_pa.open.return_value = mock_stream
        mock_pa.get_sample_size.return_value = 2
        mock_pyaudio.return_value = mock_pa
        
        # Mock transcription
        mock_transcription = MagicMock()
        mock_transcription.text = "Hello, how are you today?"
        mock_openai_client.audio.transcriptions.create.return_value = mock_transcription
        
        # Mock agent response
        mock_memories = [{"memory": "User greets politely"}]
        mock_memg.search.return_value = mock_memories
        mock_result = MagicMock()
        mock_result.raw = "I'm doing great, thank you for asking!"
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        mock_memg.add.return_value = True
        
        # Mock TTS
        mock_tts_client.text_to_speech.convert.return_value = [b'audio_data']
        mock_pygame.mixer.music.get_busy.return_value = False
        mock_exists.return_value = True
        
        # Execute full flow
        temp_file = "test_audio.wav"
        
        # Step 1: Record audio
        record_wav(temp_file, seconds=1)
        
        # Step 2: Transcribe
        with patch('builtins.open', mock_open(read_data=b'audio_data')):
            transcribed_text = transcribe(temp_file)
        
        # Step 3: Get AI response
        with patch('voice_agent_original.USER_ID', 'test_user'):
            response = get_reply(transcribed_text)
        
        # Step 4: Speak response
        with patch('builtins.open', mock_open()):
            speak(response)
        
        # Verify the complete flow
        self.assertEqual(transcribed_text, "Hello, how are you today?")
        self.assertEqual(response, "I'm doing great, thank you for asking!")
        
        # Verify all components were called
        mock_pa.open.assert_called_once()  # Recording
        mock_openai_client.audio.transcriptions.create.assert_called_once()  # Transcription
        mock_crew_instance.kickoff.assert_called_once()  # AI response
        mock_tts_client.text_to_speech.convert.assert_called_once()  # TTS
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    @patch('voice_agent_original.openai_client')
    def test_error_recovery_flow(self, mock_openai_client, mock_crew_class, mock_memg,
                                mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test error recovery in the conversation flow."""
        from voice_agent_original import transcribe, get_reply, speak
        
        # Mock transcription failure then success
        mock_openai_client.audio.transcriptions.create.side_effect = [
            Exception("API temporarily unavailable"),
            MagicMock(text="Hello after retry")
        ]
        
        # Mock agent response with memory error
        mock_memg.search.side_effect = Exception("Memory service down")
        mock_result = MagicMock()
        mock_result.raw = "Response without memory context"
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        mock_memg.add.side_effect = Exception("Memory save failed")
        
        # Mock TTS failure
        mock_tts_client.text_to_speech.convert.side_effect = Exception("TTS service error")
        
        # Test transcription error handling
        with patch('builtins.open', mock_open(read_data=b'audio_data')):
            with self.assertRaises(Exception):
                transcribe(self.temp_audio_file.name)
        
        # Test agent with memory errors (should not raise exception)
        with patch('voice_agent_original.USER_ID', 'test_user'):
            with patch('builtins.print') as mock_print:
                response = get_reply("Hello")
                
                # Should still return response despite memory errors
                self.assertEqual(response, "Response without memory context")
                
                # Should print warnings
                mock_print.assert_any_call("💭 Memory search warning: Memory service down")
                mock_print.assert_any_call("💭 Memory addition warning: Memory save failed")
        
        # Test TTS error handling (should not raise exception)
        with patch('builtins.print') as mock_print:
            speak("Test message")
            
            # Should print error message
            mock_print.assert_any_call("🔇 TTS Error: TTS service error")
            mock_print.assert_any_call("Continuing without speech...")
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_main_loop_integration(self, mock_print, mock_getpid, mock_exists, mock_remove,
                                  mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test the main loop with multiple conversation turns."""
        from voice_agent_original import run
        
        # Mock conversation sequence
        mock_getpid.return_value = 12345
        mock_exists.return_value = True
        
        conversation_turns = [
            ("What's the weather?", "It's sunny today!"),
            ("Tell me a joke", "Why did the chicken cross the road? To get to the other side!"),
            ("What time is it?", "I don't have access to the current time."),
            ("quit", None)  # Exit conversation
        ]
        
        # Set up mock responses
        transcribe_responses = [turn[0] for turn in conversation_turns]
        get_reply_responses = [turn[1] for turn in conversation_turns if turn[1] is not None]
        
        mock_transcribe.side_effect = transcribe_responses
        mock_get_reply.side_effect = get_reply_responses
        
        # Run the main loop
        run()
        
        # Verify recording happened for each turn
        self.assertEqual(mock_record.call_count, 4)
        
        # Verify transcription happened for each turn
        self.assertEqual(mock_transcribe.call_count, 4)
        
        # Verify get_reply was called for non-quit messages
        self.assertEqual(mock_get_reply.call_count, 3)
        expected_calls = [
            unittest.mock.call("What's the weather?"),
            unittest.mock.call("Tell me a joke"),
            unittest.mock.call("What time is it?")
        ]
        mock_get_reply.assert_has_calls(expected_calls)
        
        # Verify speak was called for each response
        self.assertEqual(mock_speak.call_count, 3)
        expected_speak_calls = [
            unittest.mock.call("It's sunny today!"),
            unittest.mock.call("Why did the chicken cross the road? To get to the other side!"),
            unittest.mock.call("I don't have access to the current time.")
        ]
        mock_speak.assert_has_calls(expected_speak_calls)
        
        # Verify cleanup happened for each turn
        self.assertEqual(mock_remove.call_count, 4)
    
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    def test_memory_context_integration(self, mock_crew_class, mock_memg):
        """Test that memory context is properly integrated into agent responses."""
        from voice_agent_original import get_reply
        
        # Mock memory with conversation history
        mock_memories = [
            {"memory": "User's name is Alice"},
            {"memory": "User prefers short answers"},
            {"memory": "User is learning Python programming"}
        ]
        mock_memg.search.return_value = mock_memories
        
        # Mock agent response
        mock_result = MagicMock()
        mock_result.raw = "Hi Alice! Here's a short Python tip for you."
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        mock_memg.add.return_value = True
        
        # Make request
        with patch('voice_agent_original.USER_ID', 'alice_123'):
            response = get_reply("Can you help me with programming?")
        
        # Verify memory search was called
        mock_memg.search.assert_called_once_with(
            "Can you help me with programming?", 
            user_id='alice_123'
        )
        
        # Verify crew was created with enhanced prompt including memories
        crew_call_args = mock_crew_class.call_args[1]
        task = crew_call_args['tasks'][0]
        task_description = task.description
        
        # Should include original prompt
        self.assertIn("Can you help me with programming?", task_description)
        
        # Should include memory context
        self.assertIn("Relevant memories:", task_description)
        self.assertIn("User's name is Alice", task_description)
        self.assertIn("User prefers short answers", task_description)
        self.assertIn("User is learning Python programming", task_description)
        
        # Verify conversation was added to memory
        mock_memg.add.assert_called_once()
        add_call_args = mock_memg.add.call_args
        conversation = add_call_args[0][0]
        user_id = add_call_args[1]['user_id']
        
        self.assertEqual(user_id, 'alice_123')
        self.assertEqual(len(conversation), 2)
        self.assertEqual(conversation[0]["role"], "user")
        self.assertEqual(conversation[0]["content"], "Can you help me with programming?")
        self.assertEqual(conversation[1]["role"], "assistant")
        self.assertEqual(conversation[1]["content"], "Hi Alice! Here's a short Python tip for you.")
    
    @patch('voice_agent_original.pyaudio.PyAudio')
    def test_audio_file_format_integration(self, mock_pyaudio):
        """Test that audio recording produces properly formatted files."""
        from voice_agent_original import record_wav
        import wave
        
        # Mock PyAudio
        mock_pa = MagicMock()
        mock_stream = MagicMock()
        # Generate some fake audio data
        mock_stream.read.return_value = b'\x00\x01' * 512  # 1024 bytes of audio data
        mock_pa.open.return_value = mock_stream
        mock_pa.get_sample_size.return_value = 2
        mock_pyaudio.return_value = mock_pa
        
        # Record audio
        test_file = "integration_test.wav"
        try:
            record_wav(test_file, seconds=1)
            
            # Verify file was created and has correct format
            self.assertTrue(os.path.exists(test_file))
            
            # Check WAV file properties
            with wave.open(test_file, 'rb') as wf:
                self.assertEqual(wf.getnchannels(), 1)  # Mono
                self.assertEqual(wf.getframerate(), 44100)  # 44.1kHz sample rate
                self.assertEqual(wf.getsampwidth(), 2)  # 16-bit samples
                
                # Should have approximately 1 second of audio
                frames = wf.getnframes()
                duration = frames / wf.getframerate()
                self.assertAlmostEqual(duration, 1.0, delta=0.1)
                
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_environment_configuration_integration(self):
        """Test that environment configuration affects component behavior."""
        # Test with custom configuration
        with patch.dict(os.environ, {
            'USER_ID': 'integration_test_user',
            'RECORDING_DURATION': '3',
            'VOICE_ID': 'custom_voice_123'
        }):
            # Re-import to pick up new environment
            import importlib
            import voice_agent_original
            importlib.reload(voice_agent_original)
            
            # Verify configuration was applied
            self.assertEqual(voice_agent_original.USER_ID, 'integration_test_user')
            self.assertEqual(voice_agent_original.RECORDING_DURATION, 3)
            self.assertEqual(voice_agent_original.VOICE_ID, 'custom_voice_123')


if __name__ == '__main__':
    unittest.main() 