#!/usr/bin/env python3
"""
OpenAI Realtime API - Weather Function Calling Test

A simple test example to demonstrate weather function calling 
using text input without audio complexity.

Usage:
    python weather_test_example.py

Requirements:
    - OPENAI_API_KEY environment variable
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from websocket_client.realtime_client import RealtimeConversation


class WeatherService:
    """Mock weather service for demonstration purposes."""
    
    @staticmethod
    def get_current_weather(location: str) -> dict:
        """Get current weather for a location."""
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
        """Get weather forecast for a location."""
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


class WeatherFunctionTest:
    """Test weather function calling with the OpenAI Realtime API."""
    
    def __init__(self):
        self.client = None
        self.weather_service = WeatherService()
        self.test_active = False
        self.pending_function_call = None
        
    async def setup(self):
        """Initialize the client with weather functions."""
        try:
            # Create client
            self.client = RealtimeConversation(
                auto_connect=False,
                voice="verse",
                temperature=0.7,
                model="gpt-4o-realtime-preview-2024-12-17"
            )
            
            # Configure session with weather functions
            session_config = {
                "instructions": """
                You are a helpful weather assistant. When users ask about weather,
                use the available weather functions to provide accurate information.
                Be conversational and descriptive in your responses.
                """,
                "tools": [
                    {
                        "type": "function",
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
                            "required": ["location"]
                        }
                    },
                    {
                        "type": "function",
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
                            "required": ["location"]
                        }
                    }
                ],
                "tool_choice": "auto"
            }
            
            self.client.update_session(session_config)
            
            # Set up event handlers
            self.setup_event_handlers()
            
            # Connect
            await self.client.connect()
            
            print("✅ Connected to OpenAI Realtime API with weather functions")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup: {e}")
            return False
    
    def setup_event_handlers(self):
        """Set up event handlers."""
        
        def on_session_created(data):
            print("🆔 Session created")
        
        def on_response_completed(data):
            # Check for function calls
            response = data.get("response", {})
            output = response.get("output", [])
            
            has_function_call = False
            for item in output:
                if item.get("type") == "function_call":
                    # Store function call for processing
                    self.pending_function_call = item
                    has_function_call = True
                    break
                elif item.get("type") == "message":
                    # Print text response
                    content = item.get("content", [])
                    for part in content:
                        if part.get("type") == "text":
                            print(f"🤖 Assistant: {part.get('text', '')}")
            
            if not has_function_call:
                print("\n✅ Response completed")
                self.test_active = False
        
        def on_error(data):
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
            self.test_active = False
        
        # Register handlers
        self.client.on("session_created", on_session_created)
        self.client.on("response_completed", on_response_completed)
        self.client.on("error", on_error)
    
    async def handle_function_call(self, function_call_item):
        """Handle function calls from the assistant."""
        try:
            function_name = function_call_item.get("name")
            call_id = function_call_item.get("call_id")
            arguments_str = function_call_item.get("arguments", "{}")
            
            print(f"🔧 Function call: {function_name}")
            print(f"📋 Arguments: {arguments_str}")
            
            # Parse arguments
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError:
                print(f"❌ Invalid function arguments: {arguments_str}")
                return
            
            # Execute function
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
            
            print(f"📤 Sending function result: {result}")
            
            # Send function result back
            self.client.send_event("conversation.item.create", {
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result)
                }
            })
            
            # Request new response
            print("🎯 Requesting response with function results...")
            self.client.send_event("response.create")
            
        except Exception as e:
            print(f"❌ Error handling function call: {e}")
            self.test_active = False
    
    async def send_text_query(self, query: str):
        """Send a text query and wait for response."""
        print(f"💬 Sending query: {query}")
        
        # Send message
        self.client.send_event("conversation.item.create", {
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": query
                    }
                ]
            }
        })
        
        # Request response
        self.client.send_event("response.create")
        
        # Wait for response
        self.test_active = True
        timeout = 30  # 30 second timeout
        elapsed = 0
        
        while self.test_active and elapsed < timeout:
            # Check if there's a pending function call to process
            if self.pending_function_call:
                await self.handle_function_call(self.pending_function_call)
                self.pending_function_call = None
            
            await asyncio.sleep(0.5)
            elapsed += 0.5
        
        if elapsed >= timeout:
            print("⏰ Timeout waiting for response")
    
    async def run_tests(self):
        """Run weather function calling tests."""
        print("\n🧪 Running Weather Function Tests")
        print("=" * 50)
        
        # Test 1: Current weather
        print("\n📍 Test 1: Current Weather")
        await self.send_text_query("What's the current weather in Paris, France?")
        
        await asyncio.sleep(2)
        
        # Test 2: Weather forecast
        print("\n📍 Test 2: Weather Forecast")
        await self.send_text_query("Give me a 5-day weather forecast for Tokyo, Japan")
        
        await asyncio.sleep(2)
        
        # Test 3: Different location
        print("\n📍 Test 3: Different Location")
        await self.send_text_query("Is it raining in London right now?")
        
        print("\n✅ All tests completed!")
    
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            self.client.disconnect()
        print("🧹 Cleanup completed")
    
    async def run(self):
        """Run the complete test."""
        try:
            if not await self.setup():
                return
            
            await self.run_tests()
            
        finally:
            await self.cleanup()


def check_requirements():
    """Check if requirements are met."""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not found")
        print("💡 Set your API key: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    try:
        import websocket
    except ImportError:
        print("❌ Error: websocket-client not installed")
        print("💡 Install it with: pip install websocket-client")
        return False
    
    return True


async def main():
    """Main function."""
    print("🚀 OpenAI Realtime API - Weather Function Calling Test")
    
    if not check_requirements():
        print("\n❌ Requirements check failed")
        return
    
    print("✅ All requirements met!")
    
    # Run test
    test = WeatherFunctionTest()
    await test.run()
    
    print("👋 Test completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}") 