# Voice Agent Tests

This directory contains comprehensive tests for all components of the `voice_agent_original.py` application.

## Test Structure

The test suite is organized into focused test modules, each testing specific components:

### Core Component Tests

- **`test_recording.py`** - Tests for audio recording functionality
  - `record_wav()` function testing
  - Audio format validation
  - Duration and cleanup testing
  - PyAudio integration testing

- **`test_transcription.py`** - Tests for speech-to-text functionality
  - `transcribe()` function testing
  - OpenAI Whisper API integration
  - File handling and error scenarios
  - Multi-language support testing

- **`test_text_to_speech.py`** - Tests for text-to-speech functionality
  - `speak()` function testing
  - ElevenLabs TTS integration
  - Audio playback with pygame
  - Error handling and cleanup

- **`test_agent_logic.py`** - Tests for AI agent functionality
  - `get_reply()` function testing
  - CrewAI integration
  - Memory context handling
  - Error recovery scenarios

- **`test_main_loop.py`** - Tests for main application loop
  - `run()` function testing
  - Conversation flow management
  - Exit command handling
  - File cleanup verification

### System Tests

- **`test_configuration.py`** - Tests for application configuration
  - Environment variable handling
  - API key validation
  - Default value testing
  - Client initialization

- **`test_integration.py`** - Integration tests
  - End-to-end conversation flow
  - Component interaction testing
  - Error recovery across components
  - Memory context integration

## Running Tests

### Run All Tests

```bash
# From the tests directory
python run_all_tests.py

# Or from the project root
python tests/run_all_tests.py
```

### Run Specific Test Module

```bash
# Run a specific test file
python run_all_tests.py recording
python run_all_tests.py transcription
python run_all_tests.py text_to_speech
python run_all_tests.py agent_logic
python run_all_tests.py main_loop
python run_all_tests.py configuration
python run_all_tests.py integration
```

### Run Individual Test Files

```bash
# Run individual test files directly
python -m unittest test_recording.py
python -m unittest test_transcription.py -v
```

## Test Coverage

The test suite covers:

### ✅ Functionality Testing
- All public functions and methods
- Input validation and edge cases
- Error handling and recovery
- Configuration management

### ✅ Integration Testing
- API integrations (OpenAI, ElevenLabs, Mem0)
- Audio system integration (PyAudio, pygame)
- File system operations
- Memory management

### ✅ Error Scenarios
- API failures and timeouts
- File system errors
- Invalid input handling
- Resource cleanup on errors

### ✅ Mock Testing
- External API calls are mocked
- File system operations are mocked
- Audio hardware dependencies are mocked
- Environment variables are controlled

## Test Dependencies

Tests use Python's built-in `unittest` framework with mocking capabilities:

- `unittest.mock` for mocking external dependencies
- `tempfile` for temporary file handling
- `patch` decorators for dependency injection

## Environment Setup for Testing

No special environment setup is required for testing as all external dependencies are mocked. However, for integration testing with real APIs, you would need:

```bash
# Example .env file (not required for mocked tests)
OPENAI_API_KEY=your_openai_key
MEM0_API_KEY=your_mem0_key
ELEVENLABS_API_KEY=your_elevenlabs_key
USER_ID=test_user
RECORDING_DURATION=4
VOICE_ID=default_voice_id
```

## Test Output

The test runner provides detailed output including:

- Test execution status for each component
- Pass/fail counts and percentages
- Detailed error messages and tracebacks
- Summary statistics

Example output:
```
======================================================================
RUNNING VOICE AGENT TESTS
======================================================================
✓ Loaded tests from test_recording
✓ Loaded tests from test_transcription
...

test_record_wav_creates_file (test_recording.TestRecording) ... ok
test_transcribe_success (test_transcription.TestTranscription) ... ok
...

======================================================================
TEST SUMMARY
======================================================================
Total Tests Run: 67
Passed: 67
Failed: 0
Errors: 0
Skipped: 0

Success Rate: 100.0%
```

## Contributing

When adding new functionality to `voice_agent_original.py`:

1. Add corresponding tests to the appropriate test module
2. Follow the existing test naming conventions
3. Use mocks for external dependencies
4. Include both positive and negative test cases
5. Test error handling and edge cases
6. Update this README if adding new test modules 