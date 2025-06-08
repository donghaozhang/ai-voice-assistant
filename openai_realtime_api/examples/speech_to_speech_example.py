#!/usr/bin/env python3
"""
OpenAI Realtime API - Speech-to-Speech Example with Function Calling

This example demonstrates how to use the OpenAI Realtime API for
real-time speech-to-speech conversations with function calling capabilities.

Features:
- Real-time voice conversation
- Push-to-talk functionality
- Audio recording and playback
- Session management
- Error handling
- Weather function calling

Usage:
    python speech_to_speech_example.py

Requirements:
    - OPENAI_API_KEY environment variable
    - Microphone and speakers
    - Internet connection
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Check for required dependencies
try:
    import keyboard
except ImportError:
    print("❌ Error: 'keyboard' module not found.")
    print("💡 Install it with: pip install keyboard")
    sys.exit(1)

try:
    from websocket_client.realtime_client import RealtimeConversation
except ImportError as e:
    print(f"❌ Error importing RealtimeConversation: {e}")
    print("💡 Make sure you've installed all requirements: pip install -r requirements.txt")
    sys.exit(1)


class WeatherService:
    """Mock weather service for demonstration purposes."""
    
    @staticmethod
    def get_current_weather(location: str) -> dict:
        """
        Get current weather for a location.
        In a real implementation, this would call a weather API.
        """
        # Mock weather data
        weather_conditions = [
            "sunny", "partly cloudy", "cloudy", "light rain", 
            "heavy rain", "snow", "thunderstorm", "foggy"
        ]
        
        temperature = random.randint(-10, 35)  # Celsius
        condition = random.choice(weather_conditions)
        humidity = random.randint(30, 90)
        
        return {
            "location": location,
            "temperature": temperature,
            "condition": condition,
            "humidity": humidity,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def get_weather_forecast(location: str, days: int = 3) -> dict:
        """
        Get weather forecast for a location.
        In a real implementation, this would call a weather API.
        """
        forecast = []
        weather_conditions = [
            "sunny", "partly cloudy", "cloudy", "light rain", 
            "heavy rain", "snow", "thunderstorm"
        ]
        
        for day in range(days):
            temp_high = random.randint(15, 35)
            temp_low = random.randint(-5, temp_high - 5)
            condition = random.choice(weather_conditions)
            
            forecast.append({
                "day": day + 1,
                "high_temperature": temp_high,
                "low_temperature": temp_low,
                "condition": condition,
                "chance_of_rain": random.randint(0, 100)
            })
        
        return {
            "location": location,
            "forecast_days": days,
            "forecast": forecast,
            "timestamp": datetime.now().isoformat()
        }


class VoiceConversationDemo:
    """
    Demonstration of voice conversation using OpenAI Realtime API with function calling.
    """
    
    def __init__(self):
        self.client = None
        self.conversation_active = False
        self.speaking = False
        self.weather_service = WeatherService()
        
    async def setup(self):
        """Initialize the conversation client."""
        try:
            # Create conversation client
            self.client = RealtimeConversation(
                auto_connect=False,
                voice="verse",  # Available: alloy, echo, fable, onyx, nova, shimmer, verse
                temperature=0.7,
                model="gpt-4o-realtime-preview-2024-12-17"
            )
            
            # Set up custom instructions with weather capabilities
            instructions = """
            You are a friendly AI assistant engaged in a natural voice conversation.
            You have access to weather information and can help users with weather queries.
            
            Keep your responses conversational, concise, and engaging.
            When providing weather information, be descriptive and helpful.
            Ask follow-up questions to keep the conversation flowing.
            Respond as if you're talking to a friend.
            
            If someone asks about weather, use the available weather functions to get current 
            conditions or forecasts for the location they mention.
            """
            
            # Configure session with weather functions
            session_config = {
                "instructions": instructions,
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_current_weather",
                            "description": "Get the current weather conditions for a specific location.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "The city and state/country, e.g. 'San Francisco, CA' or 'London, UK'"
                                    }
                                },
                                "required": ["location"],
                                "additionalProperties": False
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_weather_forecast",
                            "description": "Get weather forecast for a specific location over the next few days.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "The city and state/country, e.g. 'San Francisco, CA' or 'London, UK'"
                                    },
                                    "days": {
                                        "type": "integer",
                                        "description": "Number of days for the forecast (1-7)",
                                        "minimum": 1,
                                        "maximum": 7,
                                        "default": 3
                                    }
                                },
                                "required": ["location", "days"],
                                "additionalProperties": False
                            }
                        }
                    }
                ],
                "tool_choice": "auto"
            }
            
            self.client.update_session(session_config)
            
            # Register event handlers
            self.setup_event_handlers()
            
            # Connect to the API
            await self.client.connect()
            
            print("✅ Connected to OpenAI Realtime API with weather functions")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup conversation: {e}")
            return False
    
    def setup_event_handlers(self):
        """Set up event handlers for the conversation."""
        
        def on_connected(data):
            print("🔗 Connected to OpenAI Realtime API")
        
        def on_session_created(data):
            session_id = data.get("session", {}).get("id", "unknown")
            print(f"🆔 Session created: {session_id}")
        
        def on_transcription(data):
            text = data.get("text", "")
            if text.strip():
                print(f"🎤 You said: {text}")
        
        def on_response_started(data):
            print("🤖 Assistant is responding...")
        
        def on_response_completed(data):
            # Check if this response contains function calls
            response = data.get("response", {})
            output = response.get("output", [])
            
            # Process any function calls
            for item in output:
                if item.get("type") == "function_call":
                    asyncio.create_task(self.handle_function_call(item))
                    return  # Don't show "ready for input" yet
            
            print("✅ Assistant finished responding")
            print("🎤 Ready for next input - Hold SPACE to speak")
        
        def on_recording_started(data):
            print("🔴 Recording started - speak now!")
            self.speaking = True
        
        def on_recording_stopped(data):
            print("⏹️  Recording stopped - processing...")
            self.speaking = False
        
        def on_error(data):
            error_msg = data.get("error", "Unknown error")
            print(f"❌ Error: {error_msg}")
        
        def on_disconnected(data):
            print("🔌 Disconnected from API")
            self.conversation_active = False
        
        # Register all handlers
        self.client.on("connected", on_connected)
        self.client.on("session_created", on_session_created)
        self.client.on("transcription", on_transcription)
        self.client.on("response_started", on_response_started)
        self.client.on("response_completed", on_response_completed)
        self.client.on("recording_started", on_recording_started)
        self.client.on("recording_stopped", on_recording_stopped)
        self.client.on("error", on_error)
        self.client.on("disconnected", on_disconnected)
    
    async def handle_function_call(self, function_call_item):
        """Handle function calls from the assistant."""
        try:
            function_name = function_call_item.get("name")
            call_id = function_call_item.get("call_id")
            arguments_str = function_call_item.get("arguments", "{}")
            
            print(f"🔧 Function call: {function_name}")
            print(f"📋 Arguments: {arguments_str}")
            
            # Parse function arguments
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError:
                print(f"❌ Invalid function arguments: {arguments_str}")
                return
            
            # Execute the appropriate function
            if function_name == "get_current_weather":
                location = arguments.get("location", "Unknown")
                print(f"🌤️  Getting current weather for {location}...")
                weather_data = self.weather_service.get_current_weather(location)
                result = {
                    "location": weather_data["location"],
                    "temperature": f"{weather_data['temperature']}°C",
                    "condition": weather_data["condition"],
                    "humidity": f"{weather_data['humidity']}%"
                }
                
            elif function_name == "get_weather_forecast":
                location = arguments.get("location", "Unknown")
                days = arguments.get("days", 3)
                print(f"📅 Getting {days}-day weather forecast for {location}...")
                forecast_data = self.weather_service.get_weather_forecast(location, days)
                result = {
                    "location": forecast_data["location"],
                    "forecast_days": forecast_data["forecast_days"],
                    "forecast": forecast_data["forecast"]
                }
                
            else:
                print(f"❌ Unknown function: {function_name}")
                return
            
            # Send function result back to the assistant
            print(f"📤 Sending function result...")
            self.client.send_event("conversation.item.create", {
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result)
                }
            })
            
            # Request a new response with the function results
            print("🎯 Requesting response with function results...")
            self.client.send_event("response.create")
            
        except Exception as e:
            print(f"❌ Error handling function call: {e}")
    
    def print_instructions(self):
        """Print usage instructions."""
        print("\n" + "="*60)
        print("🎙️  VOICE CONVERSATION DEMO WITH WEATHER")
        print("="*60)
        print("📋 CONTROLS:")
        print("   🔥 Hold SPACE to speak")
        print("   ⏹️  Release SPACE to stop speaking")
        print("   💬 Type 'text:' followed by your message to send text")
        print("   🚪 Type 'quit' or 'exit' to end conversation")
        print("   ❓ Type 'help' for this menu")
        print("="*60)
        print("🌤️  WEATHER FEATURES:")
        print("   - Ask for current weather: 'What's the weather in Paris?'")
        print("   - Ask for forecasts: 'Give me a 5-day forecast for Tokyo'")
        print("   - Natural language works: 'Is it raining in London?'")
        print("="*60)
        print("💡 Tips:")
        print("   - Speak clearly into your microphone")
        print("   - Wait for the assistant to finish before speaking")
        print("   - Try asking about weather in different cities")
        print("   - Keep responses natural and conversational")
        print("="*60)
    
    async def handle_keyboard_input(self):
        """Handle keyboard input for push-to-talk."""
        try:
            print("📌 Keyboard controls active - Hold SPACE to speak")
            while self.conversation_active:
                # Check for spacebar press (push-to-talk)
                if keyboard.is_pressed('space'):
                    if self.client.is_ready_for_input():
                        self.client.start_recording()
                        
                        # Wait while space is held
                        while keyboard.is_pressed('space') and self.conversation_active:
                            await asyncio.sleep(0.1)
                        
                        # Stop recording when space is released
                        if self.speaking:
                            self.client.stop_speaking()
                
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Keyboard input error: {e}")
            print("💡 Try running as administrator or check keyboard permissions")
    
    async def handle_text_commands(self):
        """Handle text input commands."""
        try:
            print("💬 Text commands available - type 'help' for options")
            
            while self.conversation_active:
                try:
                    # This is a simplified version - for a production app, you'd want 
                    # proper async input handling
                    await asyncio.sleep(1)
                    
                except KeyboardInterrupt:
                    print("\n⚠️  Stopping conversation...")
                    self.conversation_active = False
                    break
                    
        except Exception as e:
            print(f"❌ Text input error: {e}")
    
    def process_text_command(self, command: str):
        """Process text commands."""
        command = command.strip().lower()
        
        if command in ['quit', 'exit', 'q']:
            print("👋 Ending conversation...")
            self.conversation_active = False
            return True
        
        elif command == 'help':
            self.print_instructions()
            return False
        
        elif command.startswith('text:'):
            # Send text message
            message = command[5:].strip()
            if message:
                print(f"💬 Sending text: {message}")
                self.client.send_text_message(message)
            return False
        
        return False
    
    async def run_conversation(self):
        """Run the main conversation loop."""
        try:
            self.conversation_active = True
            self.print_instructions()
            
            print("\n🎉 Weather-enabled conversation started!")
            print("🎮 Controls:")
            print("   - Hold SPACE to speak")
            print("   - Press Ctrl+C to exit")
            print("   - Try asking: 'What's the weather like in New York?'")
            
            # Start keyboard handling
            keyboard_task = asyncio.create_task(self.handle_keyboard_input())
            text_task = asyncio.create_task(self.handle_text_commands())
            
            # Keep the conversation running
            try:
                while self.conversation_active:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n⚠️  Conversation interrupted by user")
                self.conversation_active = False
            
            # Cancel tasks
            keyboard_task.cancel()
            text_task.cancel()
            
        except Exception as e:
            print(f"❌ Conversation error: {e}")
        finally:
            self.conversation_active = False
    
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            if self.client.recording:
                self.client.stop_recording()
            self.client.disconnect()
        print("🧹 Cleanup completed")
    
    async def run(self):
        """Run the complete demonstration."""
        try:
            # Setup
            if not await self.setup():
                return
            
            # Run conversation
            await self.run_conversation()
            
        finally:
            # Cleanup
            await self.cleanup()


def check_requirements():
    """Check if all requirements are met."""
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not found")
        print("💡 Set your API key: export OPENAI_API_KEY='your-api-key-here'")
        print("💡 On Windows: set OPENAI_API_KEY=your-api-key-here")
        return False
    
    # Check required packages
    try:
        import pyaudio
        import websocket
        import keyboard
    except ImportError as e:
        print(f"❌ Error: Missing required package: {e}")
        print("💡 Install requirements: pip install -r requirements.txt")
        print("💡 Or install individually: pip install pyaudio websocket-client keyboard")
        return False
    
    # Check microphone access
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        # Try to open microphone
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            input=True,
            frames_per_buffer=1024
        )
        stream.close()
        p.terminate()
        
    except Exception as e:
        print(f"⚠️  Warning: Microphone access issue: {e}")
        print("💡 Make sure your microphone is connected and accessible")
        print("💡 On some systems, you may need to run as administrator")
        return False
    
    return True


async def main():
    """Main function."""
    print("🚀 Starting OpenAI Realtime API Speech-to-Speech Demo with Weather Functions")
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix the issues above and try again.")
        return
    
    print("✅ All requirements met!")
    
    # Create and run demo
    demo = VoiceConversationDemo()
    await demo.run()
    
    print("👋 Demo completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure all dependencies are installed and your API key is set") 