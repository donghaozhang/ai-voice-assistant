import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock, call
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_agent_original import run


class TestMainLoop(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_single_interaction(self, mock_print, mock_getpid, mock_exists, mock_remove, 
                                   mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test a single conversation interaction."""
        # Mock setup
        mock_getpid.return_value = 12345
        mock_transcribe.return_value = "Hello, how are you?"
        mock_get_reply.return_value = "I'm doing well, thank you!"
        mock_exists.return_value = True
        
        # Mock input that causes loop to exit after one iteration
        mock_transcribe.side_effect = ["Hello, how are you?", "quit"]
        
        run()
        
        # Verify recording was called
        self.assertEqual(mock_record.call_count, 2)  # Once for "Hello" and once for "quit"
        expected_temp_file = "temp_audio_12345.wav"
        mock_record.assert_has_calls([
            call(expected_temp_file),
            call(expected_temp_file)
        ])
        
        # Verify transcription was called
        self.assertEqual(mock_transcribe.call_count, 2)
        
        # Verify get_reply was called for non-quit message
        mock_get_reply.assert_called_once_with("Hello, how are you?")
        
        # Verify speak was called
        mock_speak.assert_called_once_with("I'm doing well, thank you!")
        
        # Verify cleanup was called
        self.assertEqual(mock_remove.call_count, 2)  # Once per iteration
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_quit_command(self, mock_print, mock_getpid, mock_exists, mock_remove,
                             mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test that 'quit' command exits the loop."""
        mock_getpid.return_value = 12345
        mock_transcribe.return_value = "quit"
        mock_exists.return_value = True
        
        run()
        
        # Should record and transcribe once
        mock_record.assert_called_once()
        mock_transcribe.assert_called_once()
        
        # Should not call get_reply or speak for quit command
        mock_get_reply.assert_not_called()
        mock_speak.assert_not_called()
        
        # Should print the transcribed text
        mock_print.assert_any_call("🗣️ You said: quit")
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_exit_command(self, mock_print, mock_getpid, mock_exists, mock_remove,
                             mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test that 'exit' command also exits the loop."""
        mock_getpid.return_value = 12345
        mock_transcribe.return_value = "exit"
        mock_exists.return_value = True
        
        run()
        
        # Should record and transcribe once
        mock_record.assert_called_once()
        mock_transcribe.assert_called_once()
        
        # Should not call get_reply or speak for exit command
        mock_get_reply.assert_not_called()
        mock_speak.assert_not_called()
        
        # Should print the transcribed text
        mock_print.assert_any_call("🗣️ You said: exit")
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_case_insensitive_quit(self, mock_print, mock_getpid, mock_exists, mock_remove,
                                      mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test that quit commands are case insensitive."""
        mock_getpid.return_value = 12345
        mock_transcribe.return_value = "QUIT"
        mock_exists.return_value = True
        
        run()
        
        # Should exit on uppercase QUIT
        mock_record.assert_called_once()
        mock_transcribe.assert_called_once()
        mock_get_reply.assert_not_called()
        mock_speak.assert_not_called()
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_whitespace_handling(self, mock_print, mock_getpid, mock_exists, mock_remove,
                                    mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test that whitespace is properly stripped from transcription."""
        mock_getpid.return_value = 12345
        mock_transcribe.side_effect = ["  Hello there  ", "quit"]
        mock_get_reply.return_value = "Hello back!"
        mock_exists.return_value = True
        
        run()
        
        # Should process the trimmed text
        mock_print.assert_any_call("🗣️ You said:   Hello there  ")  # Shows original with spaces
        mock_get_reply.assert_called_with("Hello there")  # But processes trimmed version
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_file_cleanup_on_error(self, mock_print, mock_getpid, mock_exists, mock_remove,
                                      mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test that temporary file is cleaned up even when errors occur."""
        mock_getpid.return_value = 12345
        mock_transcribe.side_effect = Exception("Transcription failed")
        mock_exists.return_value = True
        
        # Should not raise exception, should clean up and continue
        try:
            # Mock the exception handling by making transcribe fail then succeed with quit
            mock_transcribe.side_effect = [Exception("Transcription failed"), "quit"]
            run()
        except Exception:
            pass  # Expected to continue despite error
        
        # File cleanup should still happen
        mock_remove.assert_called()
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_file_cleanup_when_not_exists(self, mock_print, mock_getpid, mock_exists, mock_remove,
                                             mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test file cleanup behavior when temp file doesn't exist."""
        mock_getpid.return_value = 12345
        mock_transcribe.return_value = "quit"
        mock_exists.return_value = False  # File doesn't exist
        
        run()
        
        # Should check existence but not try to remove
        mock_exists.assert_called()
        mock_remove.assert_not_called()
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_temp_file_naming(self, mock_print, mock_getpid, mock_exists, mock_remove,
                                 mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test that temporary file uses correct naming pattern."""
        mock_getpid.return_value = 99999
        mock_transcribe.return_value = "quit"
        mock_exists.return_value = True
        
        run()
        
        # Verify temp file name includes PID
        expected_filename = "temp_audio_99999.wav"
        mock_record.assert_called_with(expected_filename)
        mock_transcribe.assert_called_with(expected_filename)
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_empty_transcription(self, mock_print, mock_getpid, mock_exists, mock_remove,
                                    mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test handling of empty transcription."""
        mock_getpid.return_value = 12345
        mock_transcribe.side_effect = ["", "quit"]  # Empty string then quit
        mock_get_reply.return_value = "I didn't hear anything."
        mock_exists.return_value = True
        
        run()
        
        # Should process empty string normally
        mock_get_reply.assert_called_with("")
        mock_speak.assert_called_with("I didn't hear anything.")
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_multiple_interactions(self, mock_print, mock_getpid, mock_exists, mock_remove,
                                      mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test multiple conversation turns before quitting."""
        mock_getpid.return_value = 12345
        mock_transcribe.side_effect = [
            "What's the weather?",
            "Tell me a joke",
            "quit"
        ]
        mock_get_reply.side_effect = [
            "It's sunny today!",
            "Why did the chicken cross the road?"
        ]
        mock_exists.return_value = True
        
        run()
        
        # Should have 3 recording attempts
        self.assertEqual(mock_record.call_count, 3)
        
        # Should have 2 get_reply calls (not for quit)
        self.assertEqual(mock_get_reply.call_count, 2)
        mock_get_reply.assert_has_calls([
            call("What's the weather?"),
            call("Tell me a joke")
        ])
        
        # Should have 2 speak calls
        self.assertEqual(mock_speak.call_count, 2)
        mock_speak.assert_has_calls([
            call("It's sunny today!"),
            call("Why did the chicken cross the road?")
        ])
    
    @patch('voice_agent_original.speak')
    @patch('voice_agent_original.get_reply')
    @patch('voice_agent_original.transcribe')
    @patch('voice_agent_original.record_wav')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.os.getpid')
    @patch('builtins.print')
    def test_run_initial_message(self, mock_print, mock_getpid, mock_exists, mock_remove,
                                mock_record, mock_transcribe, mock_get_reply, mock_speak):
        """Test that the initial welcome message is displayed."""
        mock_getpid.return_value = 12345
        mock_transcribe.return_value = "quit"
        mock_exists.return_value = True
        
        run()
        
        # Should print welcome message
        mock_print.assert_any_call("🎙️ Speak to your AI assistant (say 'quit' to exit)")


if __name__ == '__main__':
    unittest.main() 