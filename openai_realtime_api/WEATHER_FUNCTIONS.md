# Weather Function Calling with OpenAI Realtime API

This documentation explains how to use function calling with the OpenAI Realtime API to create a weather-enabled voice assistant.

## Overview

The OpenAI Realtime API supports function calling, which allows the AI assistant to execute custom code to extend its capabilities. In this implementation, we've added weather functions that the assistant can call to provide current weather information and forecasts.

## Features

- **Current Weather**: Get current weather conditions for any location
- **Weather Forecasts**: Get multi-day weather forecasts (1-7 days)
- **Natural Language**: Users can ask in natural language like "Is it raining in London?"
- **Voice Integration**: Works with both voice and text input
- **Mock Weather Service**: Includes a demonstration weather service

## How It Works

### 1. Function Definition

Functions are defined in the session configuration with JSON Schema:

```python
session_config = {
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
                        "description": "The city and state/country, e.g. 'San Francisco, CA'"
                    }
                },
                "required": ["location"]
            }
        }
    ],
    "tool_choice": "auto"
}
```

### 2. Function Detection

When the assistant decides to call a function, it returns a response with `type: "function_call"`:

```python
def on_response_completed(data):
    response = data.get("response", {})
    output = response.get("output", [])
    
    for item in output:
        if item.get("type") == "function_call":
            # Handle the function call
            asyncio.create_task(self.handle_function_call(item))
```

### 3. Function Execution

The client executes the requested function and sends results back:

```python
async def handle_function_call(self, function_call_item):
    function_name = function_call_item.get("name")
    call_id = function_call_item.get("call_id")
    arguments = json.loads(function_call_item.get("arguments", "{}"))
    
    # Execute the function
    if function_name == "get_current_weather":
        location = arguments.get("location")
        result = self.weather_service.get_current_weather(location)
    
    # Send result back to assistant
    self.client.send_event("conversation.item.create", {
        "item": {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps(result)
        }
    })
    
    # Request new response with function results
    self.client.send_event("response.create")
```

## Available Weather Functions

### get_current_weather

Gets current weather conditions for a location.

**Parameters:**
- `location` (string, required): City and state/country (e.g., "Paris, France")

**Returns:**
```json
{
    "location": "Paris, France",
    "temperature": "22°C",
    "condition": "partly cloudy",
    "humidity": "65%"
}
```

### get_weather_forecast

Gets weather forecast for multiple days.

**Parameters:**
- `location` (string, required): City and state/country
- `days` (integer, optional): Number of forecast days (1-7, default: 3)

**Returns:**
```json
{
    "location": "Tokyo, Japan",
    "forecast_days": 5,
    "forecast": [
        {
            "day": 1,
            "high_temperature": 28,
            "low_temperature": 18,
            "condition": "sunny",
            "chance_of_rain": 10
        }
    ]
}
```

## Usage Examples

### Voice Queries

Users can ask natural language questions:

- "What's the weather like in New York?"
- "Give me a 5-day forecast for Tokyo"
- "Is it raining in London right now?"
- "How's the weather in Paris, France?"

### Text Queries

For testing, you can also send text messages:

```python
# Send a text weather query
client.send_text_message("What's the current weather in San Francisco?")
```

## Running the Examples

### 1. Full Voice Example

Run the complete speech-to-speech example with weather functions:

```bash
conda activate ai-researcher
cd openai_realtime_api/examples
python speech_to_speech_example.py
```

**Features:**
- Hold SPACE to speak
- Ask weather questions naturally
- Get spoken responses with weather information

### 2. Text-Only Test

Run a simplified test without audio complexity:

```bash
conda activate ai-researcher
cd openai_realtime_api/examples
python weather_test_example.py
```

**Features:**
- Tests weather functions with predefined queries
- Shows function call flow and responses
- Easier for debugging and development

## Implementation Details

### Weather Service

The included `WeatherService` class provides mock weather data:

```python
class WeatherService:
    @staticmethod
    def get_current_weather(location: str) -> dict:
        # Returns mock weather data with:
        # - Random temperature (-10°C to 35°C)
        # - Random weather condition
        # - Random humidity (30-90%)
        # - Current timestamp
        
    @staticmethod
    def get_weather_forecast(location: str, days: int = 3) -> dict:
        # Returns mock forecast data with:
        # - Daily high/low temperatures
        # - Weather conditions
        # - Chance of rain
```

### Real Weather API Integration

To use real weather data, replace the mock service with actual API calls:

```python
import requests

class RealWeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, location: str) -> dict:
        url = f"{self.base_url}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        return {
            "location": location,
            "temperature": f"{data['main']['temp']}°C",
            "condition": data['weather'][0]['description'],
            "humidity": f"{data['main']['humidity']}%"
        }
```

### Error Handling

The implementation includes comprehensive error handling:

- **Invalid JSON**: Handles malformed function arguments
- **Unknown Functions**: Gracefully handles unexpected function calls
- **Network Errors**: Manages API connection issues
- **Timeouts**: Prevents hanging on unresponsive calls

### Event Flow

The complete function calling flow:

1. **User Input**: "What's the weather in Paris?"
2. **Assistant Analysis**: Determines weather function needed
3. **Function Call**: Returns function name and arguments
4. **Client Execution**: Runs weather service function
5. **Result Submission**: Sends weather data back to assistant
6. **Final Response**: Assistant generates natural language response

## Advanced Features

### Multiple Function Calls

The assistant can make multiple function calls in sequence:

```
User: "Compare the weather in New York and London"
→ get_current_weather(location="New York, NY")
→ get_current_weather(location="London, UK")
→ Final response comparing both locations
```

### Context Awareness

The assistant maintains context across function calls:

```
User: "What's the weather in Tokyo?"
Assistant: [Calls weather function, provides current weather]
User: "What about the forecast?"
Assistant: [Calls forecast function for Tokyo, remembers location]
```

### Custom Instructions

You can customize how the assistant uses weather functions:

```python
instructions = """
You are a weather expert assistant. When providing weather information:
- Always mention the temperature in both Celsius and Fahrenheit
- Provide clothing recommendations based on conditions
- Include warnings for severe weather
- Be enthusiastic about good weather and supportive during bad weather
"""
```

## Troubleshooting

### Common Issues

1. **Function Not Called**: 
   - Check function description clarity
   - Ensure `tool_choice: "auto"` is set
   - Verify user query is weather-related

2. **Invalid Arguments**:
   - Check JSON schema validation
   - Ensure location format is clear
   - Handle missing required parameters

3. **Response Timeout**:
   - Increase timeout duration
   - Check network connectivity
   - Verify function execution speed

### Debug Mode

Enable verbose logging to see function call details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show:
- Function call detection
- Argument parsing
- Function execution results
- Response generation

## Next Steps

1. **Real Weather API**: Replace mock service with OpenWeatherMap or similar
2. **Location Services**: Add GPS/IP-based location detection
3. **Weather Alerts**: Implement severe weather notifications
4. **Historical Data**: Add functions for weather history
5. **Extended Forecasts**: Support longer-term forecasts
6. **Multiple Locations**: Track weather for multiple saved locations

## Related Documentation

- [OpenAI Realtime API Function Calling](https://platform.openai.com/docs/guides/realtime-conversations#function-calling)
- [JSON Schema Reference](https://json-schema.org/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Voice Agent Setup](./README.md) 