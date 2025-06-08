import unittest
import os
import tempfile
import wave
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_agent_original import record_wav


class TestRecording(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.test_file.close()
        
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_file.name):
            os.remove(self.test_file.name)
    
    @patch('voice_agent_original.pyaudio.PyAudio')
    def test_record_wav_creates_file(self, mock_pyaudio):
        """Test that record_wav creates a valid WAV file."""
        # Mock PyAudio components
        mock_pa = MagicMock()
        mock_stream = MagicMock()
        mock_stream.read.return_value = b'\x00' * 1024  # Mock audio data
        mock_pa.open.return_value = mock_stream
        mock_pa.get_sample_size.return_value = 2
        mock_pyaudio.return_value = mock_pa
        
        # Call the function
        record_wav(self.test_file.name, seconds=1)
        
        # Check file was created
        self.assertTrue(os.path.exists(self.test_file.name))
        
        # Check file is valid WAV format
        with wave.open(self.test_file.name, 'rb') as wf:
            self.assertEqual(wf.getnchannels(), 1)  # Mono
            self.assertEqual(wf.getframerate(), 44100)  # Sample rate
            self.assertEqual(wf.getsampwidth(), 2)  # Sample width
    
    @patch('voice_agent_original.pyaudio.PyAudio')
    def test_record_wav_duration(self, mock_pyaudio):
        """Test that record_wav records for the specified duration."""
        mock_pa = MagicMock()
        mock_stream = MagicMock()
        mock_stream.read.return_value = b'\x00' * 1024
        mock_pa.open.return_value = mock_stream
        mock_pa.get_sample_size.return_value = 2
        mock_pyaudio.return_value = mock_pa
        
        # Test with 2 seconds
        record_wav(self.test_file.name, seconds=2)
        
        # Calculate expected number of reads based on duration
        expected_reads = int(44100 / 1024 * 2)
        actual_reads = mock_stream.read.call_count
        
        self.assertEqual(actual_reads, expected_reads)
    
    @patch('voice_agent_original.pyaudio.PyAudio')
    def test_record_wav_default_duration(self, mock_pyaudio):
        """Test that record_wav uses default duration when none specified."""
        mock_pa = MagicMock()
        mock_stream = MagicMock()
        mock_stream.read.return_value = b'\x00' * 1024
        mock_pa.open.return_value = mock_stream
        mock_pa.get_sample_size.return_value = 2
        mock_pyaudio.return_value = mock_pa
        
        # Call without specifying duration
        record_wav(self.test_file.name)
        
        # Should use RECORDING_DURATION (4 seconds by default)
        expected_reads = int(44100 / 1024 * 4)
        actual_reads = mock_stream.read.call_count
        
        self.assertEqual(actual_reads, expected_reads)
    
    @patch('voice_agent_original.pyaudio.PyAudio')
    def test_record_wav_audio_format(self, mock_pyaudio):
        """Test that record_wav uses correct audio format settings."""
        mock_pa = MagicMock()
        mock_stream = MagicMock()
        mock_stream.read.return_value = b'\x00' * 1024
        mock_pa.open.return_value = mock_stream
        mock_pa.get_sample_size.return_value = 2
        mock_pyaudio.return_value = mock_pa
        
        record_wav(self.test_file.name, seconds=1)
        
        # Verify PyAudio was called with correct parameters
        mock_pa.open.assert_called_once()
        call_args = mock_pa.open.call_args[1]
        
        self.assertEqual(call_args['channels'], 1)
        self.assertEqual(call_args['rate'], 44100)
        self.assertEqual(call_args['input'], True)
        self.assertEqual(call_args['frames_per_buffer'], 1024)
    
    @patch('voice_agent_original.pyaudio.PyAudio')
    def test_record_wav_cleanup(self, mock_pyaudio):
        """Test that record_wav properly cleans up audio resources."""
        mock_pa = MagicMock()
        mock_stream = MagicMock()
        mock_stream.read.return_value = b'\x00' * 1024
        mock_pa.open.return_value = mock_stream
        mock_pa.get_sample_size.return_value = 2
        mock_pyaudio.return_value = mock_pa
        
        record_wav(self.test_file.name, seconds=1)
        
        # Verify proper cleanup
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        mock_pa.terminate.assert_called_once()


if __name__ == '__main__':
    unittest.main() 