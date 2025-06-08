#!/usr/bin/env python3
"""
OpenAI Realtime API - Speech-to-Speech Example

This example demonstrates how to use the OpenAI Realtime API for
real-time speech-to-speech conversations using WebSocket connections.

Features:
- Real-time voice conversation
- Push-to-talk functionality
- Audio recording and playback
- Session management
- Error handling

Usage:
    python speech_to_speech_example.py

Requirements:
    - OPENAI_API_KEY environment variable
    - Microphone and speakers
    - Internet connection
"""

import asyncio
import os
import sys
import time
import keyboard
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from websocket_client.realtime_client import RealtimeConversation


class VoiceConversationDemo:
    """
    Demonstration of voice conversation using OpenAI Realtime API.
    """
    
    def __init__(self):
        self.client = None
        self.conversation_active = False
        self.speaking = False
        
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
            
            # Set up custom instructions
            instructions = """
            You are a friendly AI assistant engaged in a natural voice conversation.
            Keep your responses conversational, concise, and engaging.
            Ask follow-up questions to keep the conversation flowing.
            Respond as if you're talking to a friend.
            """
            
            self.client.update_session({"instructions": instructions})
            
            # Register event handlers
            self.setup_event_handlers()
            
            # Connect to the API
            await self.client.connect()
            
            print("✅ Connected to OpenAI Realtime API")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup conversation: {e}")
            return False
    
    def setup_event_handlers(self):
        """Set up event handlers for the conversation."""
        
        @self.client.on("connected")
        def on_connected(data):
            print("🔗 Connected to OpenAI Realtime API")
        
        @self.client.on("session_created")
        def on_session_created(data):
            session_id = data.get("session", {}).get("id", "unknown")
            print(f"🆔 Session created: {session_id}")
        
        @self.client.on("transcription")
        def on_transcription(data):
            text = data.get("text", "")
            if text.strip():
                print(f"🎤 You said: {text}")
        
        @self.client.on("response_started")
        def on_response_started(data):
            print("🤖 Assistant is responding...")
        
        @self.client.on("response_completed")
        def on_response_completed(data):
            print("✅ Assistant finished responding")
        
        @self.client.on("recording_started")
        def on_recording_started(data):
            print("🔴 Recording started - speak now!")
            self.speaking = True
        
        @self.client.on("recording_stopped")
        def on_recording_stopped(data):
            print("⏹️  Recording stopped - processing...")
            self.speaking = False
        
        @self.client.on("error")
        def on_error(data):
            error_msg = data.get("error", "Unknown error")
            print(f"❌ Error: {error_msg}")
        
        @self.client.on("disconnected")
        def on_disconnected(data):
            print("🔌 Disconnected from API")
            self.conversation_active = False
    
    def print_instructions(self):
        """Print usage instructions."""
        print("\n" + "="*60)
        print("🎙️  VOICE CONVERSATION DEMO")
        print("="*60)
        print("📋 CONTROLS:")
        print("   🔥 Hold SPACE to speak")
        print("   ⏹️  Release SPACE to stop speaking")
        print("   💬 Type 'text:' followed by your message to send text")
        print("   🚪 Type 'quit' or 'exit' to end conversation")
        print("   ❓ Type 'help' for this menu")
        print("="*60)
        print("💡 Tips:")
        print("   - Speak clearly into your microphone")
        print("   - Wait for the assistant to finish before speaking")
        print("   - Keep responses natural and conversational")
        print("="*60)
    
    async def handle_keyboard_input(self):
        """Handle keyboard input for push-to-talk."""
        try:
            while self.conversation_active:
                # Check for spacebar press (push-to-talk)
                if keyboard.is_pressed('space'):
                    if not self.speaking and not self.client.is_responding():
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
    
    async def handle_text_input(self):
        """Handle text input commands."""
        try:
            while self.conversation_active:
                # Use asyncio to get input without blocking
                try:
                    # Simple input handling (non-blocking would require more complex setup)
                    await asyncio.sleep(0.5)
                    
                    # Check if there's any input available
                    # This is a simplified version - in production you'd use proper async input
                    
                except KeyboardInterrupt:
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
            
            print("\n🎉 Conversation started! Hold SPACE to speak...")
            
            # Start keyboard handling
            keyboard_task = asyncio.create_task(self.handle_keyboard_input())
            
            # Keep the conversation running
            while self.conversation_active:
                await asyncio.sleep(1)
            
            # Cancel keyboard task
            keyboard_task.cancel()
            
        except KeyboardInterrupt:
            print("\n⚠️  Conversation interrupted by user")
        except Exception as e:
            print(f"❌ Conversation error: {e}")
        finally:
            self.conversation_active = False
    
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
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
        return False
    
    # Check required packages
    try:
        import pyaudio
        import websocket
        import keyboard
    except ImportError as e:
        print(f"❌ Error: Missing required package: {e}")
        print("💡 Install requirements: pip install pyaudio websocket-client keyboard")
        return False
    
    return True


async def main():
    """Main function."""
    print("🚀 Starting OpenAI Realtime API Speech-to-Speech Demo")
    
    # Check requirements
    if not check_requirements():
        return
    
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