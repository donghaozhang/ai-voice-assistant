import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_agent_original import transcribe


class TestTranscription(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.test_audio_file.write(b'fake_audio_data')
        self.test_audio_file.close()
        
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_audio_file.name):
            os.remove(self.test_audio_file.name)
    
    @patch('voice_agent_original.openai_client')
    def test_transcribe_success(self, mock_client):
        """Test successful transcription of audio file."""
        # Mock OpenAI response
        mock_transcription = MagicMock()
        mock_transcription.text = "Hello, this is a test transcription."
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        # Call transcribe function
        result = transcribe(self.test_audio_file.name)
        
        # Verify the result
        self.assertEqual(result, "Hello, this is a test transcription.")
        
        # Verify OpenAI client was called correctly
        mock_client.audio.transcriptions.create.assert_called_once()
        call_args = mock_client.audio.transcriptions.create.call_args
        self.assertEqual(call_args[1]['model'], 'whisper-1')
    
    @patch('voice_agent_original.openai_client')
    def test_transcribe_with_file_reading(self, mock_client):
        """Test that transcribe properly reads the audio file."""
        mock_transcription = MagicMock()
        mock_transcription.text = "Test transcription"
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        with patch('builtins.open', mock_open(read_data=b'audio_data')) as mock_file:
            result = transcribe('test_file.wav')
            
            # Verify file was opened in binary read mode
            mock_file.assert_called_once_with('test_file.wav', 'rb')
            
            # Verify transcription was successful
            self.assertEqual(result, "Test transcription")
    
    @patch('voice_agent_original.openai_client')
    def test_transcribe_empty_response(self, mock_client):
        """Test transcription with empty response."""
        mock_transcription = MagicMock()
        mock_transcription.text = ""
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        result = transcribe(self.test_audio_file.name)
        
        self.assertEqual(result, "")
    
    @patch('voice_agent_original.openai_client')
    def test_transcribe_whitespace_handling(self, mock_client):
        """Test transcription with whitespace in response."""
        mock_transcription = MagicMock()
        mock_transcription.text = "  Hello world with spaces  "
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        result = transcribe(self.test_audio_file.name)
        
        # The transcribe function doesn't strip whitespace, so it should return as-is
        self.assertEqual(result, "  Hello world with spaces  ")
    
    @patch('voice_agent_original.openai_client')
    def test_transcribe_model_parameter(self, mock_client):
        """Test that transcribe uses the correct Whisper model."""
        mock_transcription = MagicMock()
        mock_transcription.text = "Test"
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        transcribe(self.test_audio_file.name)
        
        # Verify the correct model is used
        call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
        self.assertEqual(call_kwargs['model'], 'whisper-1')
    
    @patch('voice_agent_original.openai_client')
    def test_transcribe_file_parameter(self, mock_client):
        """Test that the file parameter is passed correctly."""
        mock_transcription = MagicMock()
        mock_transcription.text = "Test"
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        with patch('builtins.open', mock_open(read_data=b'audio_data')) as mock_file:
            transcribe('test_audio.wav')
            
            # Verify file object is passed to OpenAI
            call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
            self.assertIn('file', call_kwargs)
            # The file object should be the return value of open()
            self.assertEqual(call_kwargs['file'], mock_file.return_value.__enter__.return_value)
    
    def test_transcribe_nonexistent_file(self):
        """Test transcription with nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            transcribe('nonexistent_file.wav')
    
    @patch('voice_agent_original.openai_client')
    def test_transcribe_api_error(self, mock_client):
        """Test handling of OpenAI API errors."""
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")
        
        with self.assertRaises(Exception) as context:
            transcribe(self.test_audio_file.name)
        
        self.assertIn("API Error", str(context.exception))
    
    @patch('voice_agent_original.openai_client')
    def test_transcribe_multilingual(self, mock_client):
        """Test transcription with non-English text."""
        mock_transcription = MagicMock()
        mock_transcription.text = "Bonjour, comment allez-vous?"
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        result = transcribe(self.test_audio_file.name)
        
        self.assertEqual(result, "Bonjour, comment allez-vous?")
    
    @patch('voice_agent_original.openai_client')
    def test_transcribe_special_characters(self, mock_client):
        """Test transcription with special characters and numbers."""
        mock_transcription = MagicMock()
        mock_transcription.text = "The price is $29.99! Call 555-123-4567."
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        result = transcribe(self.test_audio_file.name)
        
        self.assertEqual(result, "The price is $29.99! Call 555-123-4567.")


if __name__ == '__main__':
    unittest.main() 