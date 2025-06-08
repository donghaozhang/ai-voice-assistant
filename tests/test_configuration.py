import unittest
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfiguration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Store original environment to restore later
        self.original_env = os.environ.copy()
        
    def tearDown(self):
        """Restore original environment after each test."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    @patch('voice_agent_original.load_dotenv')
    def test_load_dotenv_called(self, mock_load_dotenv):
        """Test that load_dotenv is called during module import."""
        # Re-import to trigger the module-level code
        import importlib
        import voice_agent_original
        importlib.reload(voice_agent_original)
        
        mock_load_dotenv.assert_called_once()
    
    def test_required_api_keys_validation(self):
        """Test that missing API keys raise appropriate errors."""
        # Clear environment variables
        for key in ["OPENAI_API_KEY", "MEM0_API_KEY", "ELEVENLABS_API_KEY"]:
            if key in os.environ:
                del os.environ[key]
        
        # Should raise ValueError when importing with missing keys
        with self.assertRaises(ValueError) as context:
            import importlib
            import voice_agent_original
            importlib.reload(voice_agent_original)
        
        error_message = str(context.exception)
        self.assertIn("Missing required API keys", error_message)
        self.assertIn("OPENAI_API_KEY", error_message)
        self.assertIn("MEM0_API_KEY", error_message)
        self.assertIn("ELEVENLABS_API_KEY", error_message)
    
    def test_partial_missing_api_keys(self):
        """Test error when only some API keys are missing."""
        # Set only some keys
        os.environ["OPENAI_API_KEY"] = "test_openai_key"
        os.environ["MEM0_API_KEY"] = "test_mem0_key"
        # ELEVENLABS_API_KEY is missing
        if "ELEVENLABS_API_KEY" in os.environ:
            del os.environ["ELEVENLABS_API_KEY"]
        
        with self.assertRaises(ValueError) as context:
            import importlib
            import voice_agent_original
            importlib.reload(voice_agent_original)
        
        error_message = str(context.exception)
        self.assertIn("ELEVENLABS_API_KEY", error_message)
        self.assertNotIn("OPENAI_API_KEY", error_message)
        self.assertNotIn("MEM0_API_KEY", error_message)
    
    @patch('voice_agent_original.MemoryClient')
    @patch('voice_agent_original.ElevenLabs')
    @patch('voice_agent_original.OpenAI')
    def test_client_initialization_with_api_keys(self, mock_openai, mock_elevenlabs, mock_mem0):
        """Test that clients are initialized with correct API keys."""
        # Set up environment
        os.environ["OPENAI_API_KEY"] = "test_openai_key"
        os.environ["MEM0_API_KEY"] = "test_mem0_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_elevenlabs_key"
        
        # Re-import to trigger client initialization
        import importlib
        import voice_agent_original
        importlib.reload(voice_agent_original)
        
        # Verify clients were initialized with correct API keys
        mock_openai.assert_called_once_with(api_key="test_openai_key")
        mock_elevenlabs.assert_called_once_with(api_key="test_elevenlabs_key")
        mock_mem0.assert_called_once_with(api_key="test_mem0_key")
    
    def test_default_configuration_values(self):
        """Test default values for configuration variables."""
        # Set required API keys
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        
        # Remove optional config variables to test defaults
        config_vars = ["USER_ID", "RECORDING_DURATION", "VOICE_ID"]
        for var in config_vars:
            if var in os.environ:
                del os.environ[var]
        
        with patch('voice_agent_original.pygame'):
            import importlib
            import voice_agent_original
            importlib.reload(voice_agent_original)
            
            # Test default values
            self.assertEqual(voice_agent_original.USER_ID, "voice_user")
            self.assertEqual(voice_agent_original.RECORDING_DURATION, 4)
            self.assertEqual(voice_agent_original.VOICE_ID, "pNInz6obpgDQGcFmaJgB")
    
    def test_custom_configuration_values(self):
        """Test custom values from environment variables."""
        # Set all environment variables
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        os.environ["USER_ID"] = "custom_user_123"
        os.environ["RECORDING_DURATION"] = "6"
        os.environ["VOICE_ID"] = "custom_voice_id"
        
        with patch('voice_agent_original.pygame'):
            import importlib
            import voice_agent_original
            importlib.reload(voice_agent_original)
            
            # Test custom values
            self.assertEqual(voice_agent_original.USER_ID, "custom_user_123")
            self.assertEqual(voice_agent_original.RECORDING_DURATION, 6)
            self.assertEqual(voice_agent_original.VOICE_ID, "custom_voice_id")
    
    def test_recording_duration_integer_conversion(self):
        """Test that RECORDING_DURATION is properly converted to integer."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        os.environ["RECORDING_DURATION"] = "10"
        
        with patch('voice_agent_original.pygame'):
            import importlib
            import voice_agent_original
            importlib.reload(voice_agent_original)
            
            self.assertEqual(voice_agent_original.RECORDING_DURATION, 10)
            self.assertIsInstance(voice_agent_original.RECORDING_DURATION, int)
    
    @patch('voice_agent_original.pygame.mixer.init')
    @patch('builtins.print')
    def test_pygame_mixer_initialization_success(self, mock_print, mock_pygame_init):
        """Test successful pygame mixer initialization."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        
        mock_pygame_init.return_value = None  # Successful initialization
        
        import importlib
        import voice_agent_original
        importlib.reload(voice_agent_original)
        
        mock_pygame_init.assert_called_once()
        # Should not print warning on success
        mock_print.assert_not_called()
    
    @patch('voice_agent_original.pygame.mixer.init')
    @patch('builtins.print')
    def test_pygame_mixer_initialization_failure(self, mock_print, mock_pygame_init):
        """Test pygame mixer initialization failure handling."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        
        mock_pygame_init.side_effect = Exception("Pygame init failed")
        
        import importlib
        import voice_agent_original
        importlib.reload(voice_agent_original)
        
        mock_pygame_init.assert_called_once()
        mock_print.assert_called_once_with("⚠️ Warning: pygame mixer initialization failed. TTS may not work.")
    
    @patch('voice_agent_original.Agent')
    def test_agent_initialization(self, mock_agent_class):
        """Test that the agent is properly initialized."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        
        with patch('voice_agent_original.pygame'):
            import importlib
            import voice_agent_original
            importlib.reload(voice_agent_original)
            
            # Verify agent was created with correct parameters
            mock_agent_class.assert_called_once_with(
                role="Voice Assistant",
                goal="Help the user and remember things.",
                backstory="You are a helpful voice assistant that can remember conversations and provide personalized responses."
            )
    
    def test_environment_variable_types(self):
        """Test that environment variables are properly typed."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        os.environ["USER_ID"] = "test_user"
        os.environ["RECORDING_DURATION"] = "8"
        os.environ["VOICE_ID"] = "test_voice"
        
        with patch('voice_agent_original.pygame'):
            import importlib
            import voice_agent_original
            importlib.reload(voice_agent_original)
            
            # Check types
            self.assertIsInstance(voice_agent_original.USER_ID, str)
            self.assertIsInstance(voice_agent_original.RECORDING_DURATION, int)
            self.assertIsInstance(voice_agent_original.VOICE_ID, str)
    
    def test_invalid_recording_duration(self):
        """Test handling of invalid RECORDING_DURATION values."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        os.environ["RECORDING_DURATION"] = "invalid_number"
        
        with patch('voice_agent_original.pygame'):
            with self.assertRaises(ValueError):
                import importlib
                import voice_agent_original
                importlib.reload(voice_agent_original)


if __name__ == '__main__':
    unittest.main() 