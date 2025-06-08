#!/usr/bin/env python3
"""
OpenAI Realtime API - Weather Function Calling (Chat Completions Format)

This example demonstrates weather function calling using the Chat Completions API
function calling format with strict mode and proper schema structure.

Features:
- Chat Completions API compatible function schemas
- Strict mode enabled with additionalProperties: false
- Proper required fields handling
- Enhanced error handling

Usage:
    python weather_chat_completion_example.py

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
    """Mock weather service following Chat Completions API format."""
    
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
        wind_speed = random.randint(0, 25)
        
        return {
            "location": location,
            "temperature": temperature,
            "condition": condition,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "units": "metric",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def get_weather_forecast(location: str, days: int) -> dict:
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
                "date": datetime.now().strftime(f"%Y-%m-%d"),
                "high_temperature": temp_high,
                "low_temperature": temp_low,
                "condition": condition,
                "chance_of_rain": random.randint(0, 100),
                "wind_speed": random.randint(5, 20)
            })
        
        return {
            "location": location,
            "forecast_days": days,
            "forecast": forecast,
            "units": "metric",
            "timestamp": datetime.now().isoformat()
        }


class ChatCompletionWeatherDemo:
    """Weather function calling using Chat Completions API format."""
    
    def __init__(self):
        self.client = None
        self.weather_service = WeatherService()
        self.test_active = False
        self.pending_function_call = None
        
    async def setup(self):
        """Initialize the client with Chat Completions API format."""
        try:
            # Create client
            self.client = RealtimeConversation(
                auto_connect=False,
                voice="verse",
                temperature=0.7,
                model="gpt-4o-realtime-preview-2024-12-17"
            )
            
            # Configure session with Chat Completions API format
            session_config = {
                "instructions": """
                You are a professional weather assistant with access to real-time weather data.
                When users ask about weather, use the available weather functions to provide 
                accurate and detailed information.
                
                Always format temperature responses clearly and include relevant details like
                humidity, wind speed, and conditions. Be conversational and helpful.
                """,
                "tools": [
                    {
                        "type": "function",
                        "name": "get_current_weather",
                        "description": "Get the current weather conditions for a specific location including temperature, humidity, wind speed, and conditions.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The city and state/country in the format 'City, Country' (e.g., 'Paris, France' or 'New York, NY, USA')"
                                }
                            },
                            "required": ["location"],
                            "additionalProperties": False
                        }
                    },
                    {
                        "type": "function",
                        "name": "get_weather_forecast",
                        "description": "Get detailed weather forecast for a specific location over multiple days including daily highs, lows, conditions, and precipitation chances.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The city and state/country in the format 'City, Country' (e.g., 'Paris, France' or 'New York, NY, USA')"
                                },
                                "days": {
                                    "type": "integer",
                                    "description": "Number of days for the forecast",
                                    "minimum": 1,
                                    "maximum": 7
                                }
                            },
                            "required": ["location", "days"],
                            "additionalProperties": False
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
            
            print("✅ Connected to OpenAI Realtime API with Chat Completions format")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup: {e}")
            return False
    
    def setup_event_handlers(self):
        """Set up event handlers."""
        
        def on_session_created(data):
            print("🆔 Session created with Chat Completions API format")
        
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
            error_msg = data.get("error", {})
            if isinstance(error_msg, dict):
                error_text = error_msg.get("message", "Unknown error")
            else:
                error_text = str(error_msg)
            print(f"❌ Error: {error_text}")
            self.test_active = False
        
        # Register handlers
        self.client.on("session_created", on_session_created)
        self.client.on("response_completed", on_response_completed)
        self.client.on("error", on_error)
    
    async def handle_function_call(self, function_call_item):
        """Handle function calls using Chat Completions format."""
        try:
            function_name = function_call_item.get("name")
            call_id = function_call_item.get("call_id")
            arguments_str = function_call_item.get("arguments", "{}")
            
            print(f"🔧 Function call: {function_name}")
            print(f"📋 Arguments: {arguments_str}")
            
            # Parse arguments with validation
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid function arguments JSON: {e}")
                return
            
            # Validate required parameters
            if function_name == "get_current_weather":
                if "location" not in arguments:
                    print("❌ Missing required parameter: location")
                    return
                location = arguments["location"]
                print(f"🌤️  Getting current weather for {location}...")
                weather_data = self.weather_service.get_current_weather(location)
                
                # Format result according to Chat Completions format
                result = {
                    "success": True,
                    "location": weather_data["location"],
                    "current_conditions": {
                        "temperature": f"{weather_data['temperature']}°C",
                        "condition": weather_data["condition"],
                        "humidity": f"{weather_data['humidity']}%",
                        "wind_speed": f"{weather_data['wind_speed']} km/h"
                    },
                    "timestamp": weather_data["timestamp"]
                }
                
            elif function_name == "get_weather_forecast":
                if "location" not in arguments or "days" not in arguments:
                    print("❌ Missing required parameters: location and/or days")
                    return
                location = arguments["location"]
                days = arguments["days"]
                
                # Validate days parameter
                if not isinstance(days, int) or days < 1 or days > 7:
                    print("❌ Invalid days parameter: must be integer between 1 and 7")
                    return
                
                print(f"📅 Getting {days}-day weather forecast for {location}...")
                forecast_data = self.weather_service.get_weather_forecast(location, days)
                
                # Format result according to Chat Completions format
                result = {
                    "success": True,
                    "location": forecast_data["location"],
                    "forecast_days": forecast_data["forecast_days"],
                    "forecast": forecast_data["forecast"],
                    "timestamp": forecast_data["timestamp"]
                }
                
            else:
                print(f"❌ Unknown function: {function_name}")
                result = {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
            
            print(f"📤 Sending function result...")
            
            # Send function result back using Chat Completions format
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
        """Run Chat Completions API format tests."""
        print("\n🧪 Running Chat Completions API Format Weather Tests")
        print("=" * 60)
        
        # Test 1: Current weather with detailed response
        print("\n📍 Test 1: Current Weather (Detailed)")
        await self.send_text_query("What's the current weather in Tokyo, Japan? Include all details.")
        
        await asyncio.sleep(2)
        
        # Test 2: Weather forecast with specific days
        print("\n📍 Test 2: Weather Forecast (7 days)")
        await self.send_text_query("Give me a detailed 7-day weather forecast for London, UK")
        
        await asyncio.sleep(2)
        
        # Test 3: Comparison query
        print("\n📍 Test 3: Weather Comparison")
        await self.send_text_query("Compare the current weather in New York and Paris")
        
        await asyncio.sleep(2)
        
        # Test 4: Natural language query
        print("\n📍 Test 4: Natural Language Query")
        await self.send_text_query("Should I bring an umbrella if I'm going to Berlin tomorrow?")
        
        print("\n✅ All Chat Completions API format tests completed!")
    
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            self.client.disconnect()
        print("🧹 Cleanup completed")
    
    async def run(self):
        """Run the complete demonstration."""
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
    print("🚀 OpenAI Realtime API - Chat Completions Format Weather Demo")
    
    if not check_requirements():
        print("\n❌ Requirements check failed")
        return
    
    print("✅ All requirements met!")
    
    # Run demonstration
    demo = ChatCompletionWeatherDemo()
    await demo.run()
    
    print("👋 Chat Completions format demo completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}") 