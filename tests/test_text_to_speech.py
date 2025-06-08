import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock, call
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_agent_original import speak


class TestTextToSpeech(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_text = "Hello, this is a test message."
        
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    def test_speak_success(self, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test successful text-to-speech conversion and playback."""
        # Mock TTS client
        mock_audio_data = [b'audio_chunk_1', b'audio_chunk_2']
        mock_tts_client.text_to_speech.convert.return_value = mock_audio_data
        
        # Mock pygame mixer
        mock_pygame.mixer.music.get_busy.side_effect = [True, True, False]  # Busy then not busy
        mock_pygame.time.wait = MagicMock()
        
        # Mock file operations
        mock_exists.return_value = True
        
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            speak(self.test_text)
            
            # Verify TTS client was called
            mock_tts_client.text_to_speech.convert.assert_called_once_with(
                text=self.test_text, 
                voice_id=unittest.mock.ANY
            )
            
            # Verify file was written
            mock_file.assert_called()
            handle = mock_file()
            expected_calls = [call(b'audio_chunk_1'), call(b'audio_chunk_2')]
            handle.write.assert_has_calls(expected_calls)
            
            # Verify pygame operations
            mock_pygame.mixer.music.load.assert_called_once()
            mock_pygame.mixer.music.play.assert_called_once()
            
            # Verify cleanup
            mock_remove.assert_called_once()
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    def test_speak_with_voice_id(self, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test that speak uses the correct voice ID."""
        mock_tts_client.text_to_speech.convert.return_value = [b'audio_data']
        mock_pygame.mixer.music.get_busy.return_value = False
        mock_exists.return_value = True
        
        with patch('builtins.open', unittest.mock.mock_open()):
            speak(self.test_text)
            
            # Verify voice ID is used (from VOICE_ID environment variable)
            call_kwargs = mock_tts_client.text_to_speech.convert.call_args[1]
            self.assertIn('voice_id', call_kwargs)
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    def test_speak_empty_text(self, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test speak with empty text."""
        mock_tts_client.text_to_speech.convert.return_value = [b'']
        mock_pygame.mixer.music.get_busy.return_value = False
        mock_exists.return_value = True
        
        with patch('builtins.open', unittest.mock.mock_open()):
            speak("")
            
            # Should still call TTS client
            mock_tts_client.text_to_speech.convert.assert_called_once_with(
                text="", 
                voice_id=unittest.mock.ANY
            )
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    def test_speak_long_text(self, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test speak with long text."""
        long_text = "This is a very long text message that should be converted to speech. " * 10
        mock_tts_client.text_to_speech.convert.return_value = [b'long_audio_data']
        mock_pygame.mixer.music.get_busy.return_value = False
        mock_exists.return_value = True
        
        with patch('builtins.open', unittest.mock.mock_open()):
            speak(long_text)
            
            mock_tts_client.text_to_speech.convert.assert_called_once_with(
                text=long_text, 
                voice_id=unittest.mock.ANY
            )
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    def test_speak_playback_waiting(self, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test that speak waits for playback to finish."""
        mock_tts_client.text_to_speech.convert.return_value = [b'audio_data']
        # Simulate busy state changing to not busy
        mock_pygame.mixer.music.get_busy.side_effect = [True, True, True, False]
        mock_exists.return_value = True
        
        with patch('builtins.open', unittest.mock.mock_open()):
            speak(self.test_text)
            
            # Verify wait was called multiple times while busy
            self.assertEqual(mock_pygame.time.wait.call_count, 3)
            mock_pygame.time.wait.assert_called_with(100)
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    def test_speak_file_cleanup_when_exists(self, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test that temporary file is cleaned up when it exists."""
        mock_tts_client.text_to_speech.convert.return_value = [b'audio_data']
        mock_pygame.mixer.music.get_busy.return_value = False
        mock_exists.return_value = True
        
        with patch('builtins.open', unittest.mock.mock_open()):
            speak(self.test_text)
            
            # Verify file existence check and removal
            mock_exists.assert_called()
            mock_remove.assert_called_once()
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    def test_speak_file_cleanup_when_not_exists(self, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test file cleanup when file doesn't exist."""
        mock_tts_client.text_to_speech.convert.return_value = [b'audio_data']
        mock_pygame.mixer.music.get_busy.return_value = False
        mock_exists.return_value = False
        
        with patch('builtins.open', unittest.mock.mock_open()):
            speak(self.test_text)
            
            # File should be checked but not removed
            mock_exists.assert_called()
            mock_remove.assert_not_called()
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    @patch('builtins.print')
    def test_speak_tts_error_handling(self, mock_print, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test error handling when TTS fails."""
        mock_tts_client.text_to_speech.convert.side_effect = Exception("TTS API Error")
        
        # Should not raise exception, should print error
        speak(self.test_text)
        
        # Verify error message was printed
        mock_print.assert_any_call("🔇 TTS Error: TTS API Error")
        mock_print.assert_any_call("Continuing without speech...")
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    @patch('builtins.print')
    def test_speak_pygame_error_handling(self, mock_print, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test error handling when pygame fails."""
        mock_tts_client.text_to_speech.convert.return_value = [b'audio_data']
        mock_pygame.mixer.music.load.side_effect = Exception("Pygame Error")
        mock_exists.return_value = True
        
        with patch('builtins.open', unittest.mock.mock_open()):
            speak(self.test_text)
            
            # Should handle error gracefully
            mock_print.assert_any_call("🔇 TTS Error: Pygame Error")
            mock_print.assert_any_call("Continuing without speech...")
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    def test_speak_temp_file_naming(self, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test that temporary file uses correct naming pattern."""
        mock_tts_client.text_to_speech.convert.return_value = [b'audio_data']
        mock_pygame.mixer.music.get_busy.return_value = False
        mock_exists.return_value = True
        
        with patch('voice_agent_original.os.getpid', return_value=12345):
            with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
                speak(self.test_text)
                
                # Verify temp file name includes PID
                expected_filename = "temp_tts_12345.mp3"
                mock_file.assert_called_with(expected_filename, 'wb')
                mock_pygame.mixer.music.load.assert_called_with(expected_filename)
    
    @patch('voice_agent_original.pygame')
    @patch('voice_agent_original.os.remove')
    @patch('voice_agent_original.os.path.exists')
    @patch('voice_agent_original.tts_client')
    def test_speak_special_characters(self, mock_tts_client, mock_exists, mock_remove, mock_pygame):
        """Test speak with text containing special characters."""
        special_text = "Hello! How are you? I'm fine. Cost: $29.99 (50% off!)"
        mock_tts_client.text_to_speech.convert.return_value = [b'audio_data']
        mock_pygame.mixer.music.get_busy.return_value = False
        mock_exists.return_value = True
        
        with patch('builtins.open', unittest.mock.mock_open()):
            speak(special_text)
            
            mock_tts_client.text_to_speech.convert.assert_called_once_with(
                text=special_text, 
                voice_id=unittest.mock.ANY
            )


if __name__ == '__main__':
    unittest.main() 