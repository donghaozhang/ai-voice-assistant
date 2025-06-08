#!/usr/bin/env python3
"""
Ephemeral Token Server for OpenAI Realtime API

This server generates ephemeral API tokens for secure client-side connections
to the OpenAI Realtime API via WebRTC. Ephemeral tokens expire after 1 minute
and provide a secure way to authenticate client applications without exposing
your main API key.

Usage:
    python ephemeral_token_server.py

The server will start on http://localhost:3000 and provide a /session endpoint
that returns ephemeral tokens.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for browser clients

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

OPENAI_API_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-realtime-preview-2024-12-17"
DEFAULT_VOICE = "verse"

# Token cache to avoid unnecessary API calls
token_cache: Dict[str, Dict[str, Any]] = {}
CACHE_DURATION = 50  # seconds (tokens expire in 60s, cache for 50s)


def clean_token_cache():
    """Remove expired tokens from cache."""
    current_time = time.time()
    expired_keys = [
        key for key, data in token_cache.items()
        if current_time - data["created_at"] > CACHE_DURATION
    ]
    for key in expired_keys:
        del token_cache[key]


def create_ephemeral_token(
    model: str = DEFAULT_MODEL,
    voice: str = DEFAULT_VOICE,
    temperature: float = 0.7,
    instructions: str = "You are a helpful AI assistant.",
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create an ephemeral token for OpenAI Realtime API.
    
    Args:
        model: Model to use for the session
        voice: Voice to use for speech synthesis
        temperature: Temperature for response generation
        instructions: System instructions for the assistant
        user_id: Optional user identifier
        
    Returns:
        Dictionary containing the ephemeral token response
    """
    try:
        # Check cache first
        cache_key = f"{model}:{voice}:{temperature}:{hash(instructions)}:{user_id}"
        clean_token_cache()
        
        if cache_key in token_cache:
            cached_data = token_cache[cache_key]
            if time.time() - cached_data["created_at"] < CACHE_DURATION:
                logger.info("Returning cached ephemeral token")
                return cached_data["response"]
        
        # Prepare request payload
        payload = {
            "model": model,
            "voice": voice,
            "temperature": temperature,
            "instructions": instructions,
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500
            }
        }
        
        if user_id:
            payload["metadata"] = {"user_id": user_id}
        
        # Make request to OpenAI API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Creating ephemeral token for model: {model}, voice: {voice}")
        
        response = requests.post(
            f"{OPENAI_API_BASE}/realtime/sessions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Cache the response
            token_cache[cache_key] = {
                "response": token_data,
                "created_at": time.time()
            }
            
            logger.info("Successfully created ephemeral token")
            return token_data
        else:
            logger.error(f"Failed to create ephemeral token: {response.status_code} - {response.text}")
            response.raise_for_status()
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error when creating ephemeral token: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when creating ephemeral token: {e}")
        raise


@app.route("/session", methods=["POST", "GET"])
def create_session():
    """
    Create a new ephemeral session token.
    
    POST body (optional):
    {
        "model": "gpt-4o-realtime-preview-2024-12-17",
        "voice": "verse",
        "temperature": 0.7,
        "instructions": "You are a helpful AI assistant.",
        "user_id": "optional_user_identifier"
    }
    
    Returns:
    {
        "id": "session_id",
        "client_secret": {
            "value": "ephemeral_token",
            "expires_at": "2024-01-01T12:01:00Z"
        },
        "model": "gpt-4o-realtime-preview-2024-12-17",
        "voice": "verse",
        ...
    }
    """
    try:
        data = request.get_json() if request.is_json else {}
        
        payload = {
            "model": data.get("model", DEFAULT_MODEL),
            "voice": data.get("voice", DEFAULT_VOICE),
            "temperature": data.get("temperature", 0.7),
            "instructions": data.get("instructions", "You are a helpful AI assistant.")
        }
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{OPENAI_API_BASE}/realtime/sessions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to create session"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/session/<session_id>", methods=["GET"])
def get_session(session_id: str):
    """
    Get information about an existing session.
    
    Note: This is a placeholder endpoint. The OpenAI API doesn't currently
    provide a way to retrieve session information after creation.
    """
    return jsonify({
        "error": "Session retrieval not supported",
        "message": "Ephemeral sessions cannot be retrieved after creation"
    }), 404


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


@app.route("/", methods=["GET"])
def index():
    """Root endpoint with API information."""
    return jsonify({
        "name": "OpenAI Realtime API Ephemeral Token Server",
        "version": "1.0.0",
        "endpoints": {
            "/session": "Create ephemeral token (POST/GET)",
            "/session/<id>": "Get session info (GET)",
            "/health": "Health check (GET)"
        },
        "documentation": "https://platform.openai.com/docs/guides/realtime",
        "models": [
            "gpt-4o-realtime-preview-2024-12-17",
            "gpt-4o-mini-realtime-preview-2024-12-17"
        ],
        "voices": [
            "alloy", "echo", "fable", "onyx", "nova", "shimmer", "verse"
        ]
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Validate environment
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY environment variable is required")
        exit(1)
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 3000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting ephemeral token server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    # Start the server
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    ) 