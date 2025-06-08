# Weather Function Calling with OpenAI Realtime API

This documentation explains how to use function calling with the OpenAI Realtime API to create a weather-enabled voice assistant, using both the original Realtime API format and the Chat Completions API format.

## Overview

The OpenAI Realtime API supports function calling, which allows the AI assistant to execute custom code to extend its capabilities. This implementation provides weather functions in two formats:

1. **Original Realtime API Format** - Native realtime function calling format
2. **Chat Completions API Format** - Compatible with Chat Completions API standards

## Key Differences Between Formats

### Chat Completions API Inspired Format (Recommended)
- **Schema Structure**: Flat structure with `"strict": true` and enhanced validation
- **Required Fields**: All parameters must be in `"required"` array
- **Validation**: `"additionalProperties": false` for strict validation
- **Type Safety**: Enhanced parameter validation and error handling
- **Compatibility**: Realtime API compatible with Chat Completions principles

### Original Realtime API Format
- **Schema Structure**: Flat structure with direct parameter definitions
- **Required Fields**: Optional parameter handling
- **Validation**: Basic validation without strict mode
- **Type Safety**: Standard parameter validation
- **Compatibility**: Native to Realtime API

## Features

- **Current Weather**: Get current weather conditions for any location
- **Weather Forecasts**: Get multi-day weather forecasts (1-7 days)
- **Natural Language**: Users can ask in natural language like "Is it raining in London?"
- **Voice Integration**: Works with both voice and text input
- **Mock Weather Service**: Includes a demonstration weather service with realistic data
- **Multiple Formats**: Support for both Chat Completions and Realtime API formats

## Files Overview

### Core Implementation Files
- `speech_to_speech_example.py` - Main voice assistant with weather functions (Chat Completions format)
- `weather_test_example.py` - Text-based weather testing example
- `weather_chat_completion_example.py` - Comprehensive Chat Completions API format example

### Function Schema Examples

#### Chat Completions API Inspired Format (Realtime API Compatible)
```json
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
        "additionalProperties": false
    },
    "strict": true
}
```

#### Original Realtime API Format
```json
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
}
```

## Available Functions

### get_current_weather(location: string)
Gets current weather conditions including:
- Temperature (Celsius)
- Weather condition (sunny, cloudy, rainy, etc.)
- Humidity percentage
- Wind speed (km/h)
- Timestamp

**Example Usage:**
- "What's the weather like in Paris?"
- "Is it raining in Tokyo right now?"
- "Tell me the current temperature in New York"

### get_weather_forecast(location: string, days: integer)
Gets multi-day weather forecast including:
- Daily high and low temperatures
- Weather conditions for each day
- Chance of precipitation
- Wind speed
- Date information

**Parameters:**
- `location`: City and country (e.g., "London, UK")
- `days`: Number of forecast days (1-7)

**Example Usage:**
- "Give me a 5-day forecast for London"
- "What will the weather be like in Berlin next week?"
- "Should I bring an umbrella to Paris tomorrow?"

## Usage Examples

### Voice Assistant Usage
1. Start the speech-to-speech example:
   ```bash
   python openai_realtime_api/examples/speech_to_speech_example.py
   ```

2. Press and hold SPACE to speak, then ask:
   - "What's the weather in Tokyo?"
   - "Give me a 3-day forecast for Paris"
   - "Is it going to rain in London tomorrow?"

### Text-Only Testing
1. Run the Chat Completions format example:
   ```bash
   python openai_realtime_api/examples/weather_chat_completion_example.py
   ```

2. Or run the basic text example:
   ```bash
   python openai_realtime_api/examples/weather_test_example.py
   ```

## Implementation Details

### Chat Completions API Inspired Format Benefits

1. **Strict Schema Validation**
   ```json
   {
       "strict": true,
       "additionalProperties": false
   }
   ```
   - Ensures function calls adhere exactly to the schema
   - Prevents invalid parameters
   - Better error handling

2. **Enhanced Parameter Validation**
   ```json
   {
       "days": {
           "type": "integer",
           "minimum": 1,
           "maximum": 7
       }
   }
   ```
   - Numeric range validation
   - Type enforcement
   - Required field validation

3. **Better Error Recovery**
   - Structured error responses
   - Clear validation messages
   - Graceful failure handling

### Function Call Flow (Chat Completions Format)

1. **User Input**: Voice or text weather query
2. **Function Detection**: AI identifies need for weather function
3. **Parameter Extraction**: AI extracts location and optional parameters
4. **Schema Validation**: Strict validation against function schema
5. **Function Execution**: Call weather service with validated parameters
6. **Result Formatting**: Format data according to Chat Completions standards
7. **Response Generation**: AI incorporates results into natural language response

### Sample Function Call Response

```json
{
    "success": true,
    "location": "Paris, France",
    "current_conditions": {
        "temperature": "18°C",
        "condition": "partly cloudy",
        "humidity": "65%",
        "wind_speed": "12 km/h"
    },
    "timestamp": "2024-01-15T14:30:00"
}
```

## Configuration

### Session Configuration (Chat Completions Format)
```python
session_config = {
    "instructions": "You are a professional weather assistant...",
    "tools": [weather_functions],
    "tool_choice": "auto"
}
```

### Error Handling
- **Invalid Location**: Graceful handling of unrecognized locations
- **Parameter Validation**: Comprehensive parameter checking
- **API Failures**: Fallback responses and error messages
- **Timeout Handling**: Request timeout management

## Testing

### Automated Tests
Run the comprehensive test suite:
```bash
python openai_realtime_api/examples/weather_chat_completion_example.py
```

### Test Cases
1. **Current Weather Queries**: Single location weather requests
2. **Forecast Requests**: Multi-day weather forecasts
3. **Comparison Queries**: Multiple location comparisons
4. **Natural Language**: Complex conversational queries

## Best Practices

### Function Schema Design (Chat Completions Format)
1. **Use Strict Mode**: Always set `"strict": true`
2. **Validate Properties**: Set `"additionalProperties": false`
3. **Required Fields**: Include all parameters in `"required"` array
4. **Clear Descriptions**: Provide detailed parameter descriptions
5. **Type Constraints**: Use `"minimum"`, `"maximum"`, `"enum"` for validation

### Error Handling
1. **Validate Inputs**: Check all required parameters before execution
2. **Graceful Failures**: Provide helpful error messages
3. **Fallback Responses**: Handle API failures gracefully
4. **User Feedback**: Clear indication of function call status

### Performance Optimization
1. **Async Operations**: Use async/await for API calls
2. **Timeout Management**: Set appropriate timeouts for function calls
3. **Resource Cleanup**: Properly dispose of resources after use
4. **Caching**: Consider caching weather data for frequently requested locations

## Migration Guide

### From Original Format to Chat Completions Format

1. **Update Schema Structure**:
   ```python
   # Old format
   {
       "type": "function",
       "name": "function_name",
       "parameters": {...}
   }
   
   # New format
   {
       "type": "function",
       "function": {
           "name": "function_name",
           "parameters": {...},
           "strict": true
       }
   }
   ```

2. **Add Strict Validation**:
   ```python
   "parameters": {
       "type": "object",
       "properties": {...},
       "required": ["all", "parameters"],
       "additionalProperties": false
   }
   ```

3. **Update Function Handling**:
   - Use `function_call_item.get("name")` instead of direct access
   - Add comprehensive parameter validation
   - Implement better error handling

## Troubleshooting

### Common Issues
1. **Function Not Called**: Check schema format and descriptions
2. **Parameter Errors**: Verify required fields and validation rules
3. **Response Timeout**: Increase timeout values for complex queries
4. **Connection Issues**: Verify API key and network connectivity

### Debug Tips
1. **Enable Logging**: Add debug prints to track function calls
2. **Validate Schemas**: Test function schemas independently
3. **Check Parameters**: Verify parameter extraction and validation
4. **Monitor Events**: Track WebSocket events for debugging

## Conclusion

The Chat Completions API format provides enhanced reliability, better error handling, and improved compatibility with OpenAI's function calling standards. It's recommended for production implementations requiring robust function calling capabilities. 