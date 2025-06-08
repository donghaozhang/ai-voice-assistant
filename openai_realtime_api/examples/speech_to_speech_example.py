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
from pathlib import Path

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
            
            print("\n🎉 Conversation started!")
            print("🎮 Controls:")
            print("   - Hold SPACE to speak")
            print("   - Press Ctrl+C to exit")
            
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
    print("🚀 Starting OpenAI Realtime API Speech-to-Speech Demo")
    
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