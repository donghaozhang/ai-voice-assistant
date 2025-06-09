import unittest
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import importlib


class TestConfiguration(unittest.TestCase):
    """Test configuration and environment variable handling."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Store original environment
        self.original_env = os.environ.copy()
        
        # Store original sys.modules entries
        self.original_modules = {}
        modules_to_store = ['voice_agent_original', 'mem0', 'openai', 'elevenlabs', 'pygame']
        for module in modules_to_store:
            if module in sys.modules:
                self.original_modules[module] = sys.modules[module]
        
        # Clear relevant environment variables
        config_vars = [
            "OPENAI_API_KEY", "MEM0_API_KEY", "ELEVENLABS_API_KEY",
            "USER_ID", "RECORDING_DURATION", "VOICE_ID"
        ]
        for var in config_vars:
            if var in os.environ:
                del os.environ[var]
        
        # Remove voice_agent_original from sys.modules if it exists
        if 'voice_agent_original' in sys.modules:
            del sys.modules['voice_agent_original']
    
    def tearDown(self):
        """Clean up after each test."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clean up sys.modules - remove any modules we may have added during tests
        modules_to_clean = ['voice_agent_original']
        for module in modules_to_clean:
            if module in sys.modules:
                del sys.modules[module]
        
        # Restore original modules
        for module, original in self.original_modules.items():
            if module in sys.modules:
                sys.modules[module] = original

    def _mock_dependencies_and_import(self):
        """Helper method to mock all dependencies and import the module safely."""
        # Create mock objects
        mock_openai = MagicMock()
        mock_elevenlabs = MagicMock()
        mock_mem0_client = MagicMock()
        mock_pygame = MagicMock()
        mock_dotenv = MagicMock()
        mock_crewai_agent = MagicMock()
        mock_crewai_crew = MagicMock()
        mock_crewai_task = MagicMock()
        mock_crewai_process = MagicMock()
        mock_pyaudio = MagicMock()
        mock_wave = MagicMock()
        mock_tempfile = MagicMock()
        
        # Mock the modules in sys.modules before importing
        sys.modules['mem0'] = MagicMock()
        sys.modules['mem0'].MemoryClient = mock_mem0_client
        sys.modules['openai'] = MagicMock()
        sys.modules['openai'].OpenAI = mock_openai
        sys.modules['elevenlabs'] = MagicMock()
        sys.modules['elevenlabs'].ElevenLabs = mock_elevenlabs
        sys.modules['pygame'] = mock_pygame
        sys.modules['pygame'].mixer = MagicMock()
        sys.modules['pygame'].mixer.init = MagicMock()
        sys.modules['pygame'].mixer.music = MagicMock()
        sys.modules['pygame'].time = MagicMock()
        sys.modules['dotenv'] = mock_dotenv
        sys.modules['dotenv'].load_dotenv = MagicMock()
        sys.modules['crewai'] = MagicMock()
        sys.modules['crewai'].Agent = mock_crewai_agent
        sys.modules['crewai'].Crew = mock_crewai_crew
        sys.modules['crewai'].Task = mock_crewai_task
        sys.modules['crewai'].Process = mock_crewai_process
        sys.modules['pyaudio'] = mock_pyaudio
        sys.modules['wave'] = mock_wave
        sys.modules['tempfile'] = mock_tempfile
        
        # Configure the mock returns
        mock_mem0_client.return_value = MagicMock()
        mock_openai.return_value = MagicMock()
        mock_elevenlabs.return_value = MagicMock()
        mock_crewai_agent.return_value = MagicMock()
        mock_crewai_agent.return_value.role = "Voice Assistant"
        mock_crewai_agent.return_value.goal = "Help the user and remember things."
        
        # Now import the module
        import voice_agent_original
        
        return voice_agent_original, {
            'mock_openai': mock_openai,
            'mock_elevenlabs': mock_elevenlabs,
            'mock_mem0_client': mock_mem0_client,
            'mock_pygame': mock_pygame,
            'mock_dotenv': mock_dotenv,
            'mock_crewai_agent': mock_crewai_agent
        }

    def test_load_dotenv_called(self):
        """Test that load_dotenv is called during module import."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        
        voice_agent, mocks = self._mock_dependencies_and_import()
        
        # Verify load_dotenv was called (through the mock)
        self.assertTrue(sys.modules['dotenv'].load_dotenv.called)

    def test_required_api_keys_validation(self):
        """Test that missing API keys raise appropriate errors."""
        # Clear environment variables
        for key in ["OPENAI_API_KEY", "MEM0_API_KEY", "ELEVENLABS_API_KEY"]:
            if key in os.environ:
                del os.environ[key]

        # Should raise ValueError when importing with missing keys
        with self.assertRaises(ValueError) as context:
            self._mock_dependencies_and_import()

        error_message = str(context.exception)
        self.assertIn("Missing required API keys", error_message)

    def test_partial_missing_api_keys(self):
        """Test error when only some API keys are missing."""
        # Set only some keys
        os.environ["OPENAI_API_KEY"] = "test_openai_key"
        os.environ["MEM0_API_KEY"] = "test_mem0_key"
        # ELEVENLABS_API_KEY is missing
        if "ELEVENLABS_API_KEY" in os.environ:
            del os.environ["ELEVENLABS_API_KEY"]

        with self.assertRaises(ValueError) as context:
            self._mock_dependencies_and_import()

        error_message = str(context.exception)
        self.assertIn("ELEVENLABS_API_KEY", error_message)

    def test_client_initialization_with_api_keys(self):
        """Test that clients are initialized with correct API keys."""
        # Set up environment
        os.environ["OPENAI_API_KEY"] = "test_openai_key"
        os.environ["MEM0_API_KEY"] = "test_mem0_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_elevenlabs_key"

        voice_agent, mocks = self._mock_dependencies_and_import()

        # Verify clients were initialized with correct API keys
        mocks['mock_openai'].assert_called_once_with(api_key="test_openai_key")
        mocks['mock_elevenlabs'].assert_called_once_with(api_key="test_elevenlabs_key")
        mocks['mock_mem0_client'].assert_called_once_with(api_key="test_mem0_key")

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

        voice_agent, mocks = self._mock_dependencies_and_import()

        # Check default values
        self.assertEqual(voice_agent.USER_ID, "voice_user")
        self.assertEqual(voice_agent.RECORDING_DURATION, 4)
        self.assertEqual(voice_agent.VOICE_ID, "pNInz6obpgDQGcFmaJgB")

    def test_custom_configuration_values(self):
        """Test custom values from environment variables."""
        # Set all environment variables
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        os.environ["USER_ID"] = "custom_user_123"
        os.environ["RECORDING_DURATION"] = "6"
        os.environ["VOICE_ID"] = "custom_voice_id"

        voice_agent, mocks = self._mock_dependencies_and_import()

        # Check custom values
        self.assertEqual(voice_agent.USER_ID, "custom_user_123")
        self.assertEqual(voice_agent.RECORDING_DURATION, 6)
        self.assertEqual(voice_agent.VOICE_ID, "custom_voice_id")

    def test_recording_duration_integer_conversion(self):
        """Test that RECORDING_DURATION is properly converted to integer."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        os.environ["RECORDING_DURATION"] = "10"

        voice_agent, mocks = self._mock_dependencies_and_import()

        self.assertEqual(voice_agent.RECORDING_DURATION, 10)
        self.assertIsInstance(voice_agent.RECORDING_DURATION, int)

    def test_pygame_mixer_initialization_success(self):
        """Test successful pygame mixer initialization."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"

        voice_agent, mocks = self._mock_dependencies_and_import()

        # Verify pygame mixer init was called
        mocks['mock_pygame'].mixer.init.assert_called_once()

    def test_pygame_mixer_initialization_failure(self):
        """Test pygame mixer initialization failure handling."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"

        # Mock all dependencies first  
        sys.modules['mem0'] = MagicMock()
        sys.modules['mem0'].MemoryClient = MagicMock(return_value=MagicMock())
        sys.modules['openai'] = MagicMock()
        sys.modules['openai'].OpenAI = MagicMock(return_value=MagicMock())
        sys.modules['elevenlabs'] = MagicMock()
        sys.modules['elevenlabs'].ElevenLabs = MagicMock(return_value=MagicMock())
        sys.modules['dotenv'] = MagicMock()
        sys.modules['dotenv'].load_dotenv = MagicMock()
        sys.modules['crewai'] = MagicMock()
        sys.modules['crewai'].Agent = MagicMock(return_value=MagicMock(
            role="Voice Assistant", 
            goal="Help the user and remember things."
        ))
        sys.modules['crewai'].Crew = MagicMock()
        sys.modules['crewai'].Task = MagicMock()
        sys.modules['crewai'].Process = MagicMock()
        sys.modules['pyaudio'] = MagicMock()
        sys.modules['wave'] = MagicMock()
        sys.modules['tempfile'] = MagicMock()
        
        # Create pygame mock that will fail on mixer.init()
        mock_pygame = MagicMock()
        mock_pygame.mixer.init.side_effect = Exception("Pygame init failed")
        sys.modules['pygame'] = mock_pygame
        
        with patch('builtins.print') as mock_print:
            import voice_agent_original

        # Verify the warning was printed
        mock_print.assert_called_with(
            "⚠️ Warning: pygame mixer initialization failed. TTS may not work."
        )

    def test_agent_initialization(self):
        """Test that the agent is properly initialized."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"

        voice_agent, mocks = self._mock_dependencies_and_import()

        # Check that agent exists and has expected properties
        self.assertIsNotNone(voice_agent.agent)
        self.assertEqual(voice_agent.agent.role, "Voice Assistant")
        self.assertIn("Help the user", voice_agent.agent.goal)

    def test_environment_variable_types(self):
        """Test that environment variables are properly typed."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        os.environ["MEM0_API_KEY"] = "test_key"
        os.environ["ELEVENLABS_API_KEY"] = "test_key"
        os.environ["USER_ID"] = "test_user"
        os.environ["RECORDING_DURATION"] = "8"
        os.environ["VOICE_ID"] = "test_voice"

        voice_agent, mocks = self._mock_dependencies_and_import()

        # Check types
        self.assertIsInstance(voice_agent.USER_ID, str)
        self.assertIsInstance(voice_agent.RECORDING_DURATION, int)
        self.assertIsInstance(voice_agent.VOICE_ID, str)
        
        # Check values
        self.assertEqual(voice_agent.USER_ID, "test_user")
        self.assertEqual(voice_agent.RECORDING_DURATION, 8)
        self.assertEqual(voice_agent.VOICE_ID, "test_voice")


if __name__ == '__main__':
    unittest.main() 