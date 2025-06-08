#!/usr/bin/env python3
"""
OpenAI Realtime API - Transcription Example

This example demonstrates how to use the OpenAI Realtime API for
real-time speech transcription using WebSocket connections.

Features:
- Real-time speech transcription
- Voice activity detection
- Transcript logging and export
- Session management
- Multiple output formats

Usage:
    python transcription_example.py

Requirements:
    - OPENAI_API_KEY environment variable
    - Microphone
    - Internet connection
"""

import asyncio
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from websocket_client.realtime_client import RealtimeTranscriber


class TranscriptionDemo:
    """
    Demonstration of real-time transcription using OpenAI Realtime API.
    """
    
    def __init__(self, output_file: str = None):
        self.client = None
        self.transcription_active = False
        self.output_file = output_file
        self.session_start = None
        self.transcripts = []
        
    async def setup(self):
        """Initialize the transcription client."""
        try:
            # Create transcription client
            self.client = RealtimeTranscriber(
                auto_connect=False
            )
            
            # Register event handlers
            self.setup_event_handlers()
            
            # Connect to the API
            await self.client.connect()
            
            print("✅ Connected to OpenAI Realtime API for transcription")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup transcription: {e}")
            return False
    
    def setup_event_handlers(self):
        """Set up event handlers for transcription."""
        
        @self.client.on("connected")
        def on_connected(data):
            print("🔗 Connected to OpenAI Realtime API")
            self.session_start = datetime.now()
        
        @self.client.on("transcription")
        def on_transcription(data):
            text = data.get("text", "")
            timestamp = data.get("timestamp", datetime.now().isoformat())
            
            if text.strip():
                # Display transcription
                time_str = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime("%H:%M:%S")
                print(f"[{time_str}] 📝 {text}")
                
                # Store transcription
                self.transcripts.append({
                    "text": text,
                    "timestamp": timestamp,
                    "session_time": (datetime.now() - self.session_start).total_seconds() if self.session_start else 0
                })
        
        @self.client.on("recording_started")
        def on_recording_started(data):
            print("🔴 Recording started - speak now!")
        
        @self.client.on("recording_stopped")
        def on_recording_stopped(data):
            print("⏹️  Recording stopped")
        
        @self.client.on("error")
        def on_error(data):
            error_msg = data.get("error", "Unknown error")
            print(f"❌ Error: {error_msg}")
        
        @self.client.on("disconnected")
        def on_disconnected(data):
            print("🔌 Disconnected from API")
            self.transcription_active = False
    
    def print_instructions(self):
        """Print usage instructions."""
        print("\n" + "="*60)
        print("🎤 REAL-TIME TRANSCRIPTION DEMO")
        print("="*60)
        print("📋 COMMANDS:")
        print("   🎙️  'start' - Start recording and transcription")
        print("   ⏹️  'stop' - Stop recording")
        print("   📄 'save' - Save transcripts to file")
        print("   🗂️  'export' - Export transcripts in different formats")
        print("   📊 'stats' - Show session statistics")
        print("   🧹 'clear' - Clear current transcripts")
        print("   🚪 'quit' or 'exit' - End session")
        print("   ❓ 'help' - Show this menu")
        print("="*60)
        print("💡 Tips:")
        print("   - Speak clearly into your microphone")
        print("   - Transcription happens in real-time")
        print("   - Use voice activity detection for automatic segmentation")
        print("="*60)
    
    def show_stats(self):
        """Show session statistics."""
        if not self.transcripts:
            print("📊 No transcripts recorded yet.")
            return
        
        total_words = sum(len(t["text"].split()) for t in self.transcripts)
        total_chars = sum(len(t["text"]) for t in self.transcripts)
        session_duration = (datetime.now() - self.session_start).total_seconds() if self.session_start else 0
        
        print("\n📊 SESSION STATISTICS")
        print("="*40)
        print(f"🕐 Session Duration: {session_duration:.1f} seconds")
        print(f"📝 Total Transcripts: {len(self.transcripts)}")
        print(f"📖 Total Words: {total_words}")
        print(f"🔤 Total Characters: {total_chars}")
        if session_duration > 0:
            print(f"⚡ Words per minute: {(total_words / session_duration * 60):.1f}")
        print("="*40)
    
    def save_transcripts(self, filename: str = None):
        """Save transcripts to file."""
        if not self.transcripts:
            print("❌ No transcripts to save.")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcription_{timestamp}.json"
        
        try:
            # Prepare data for export
            export_data = {
                "session_info": {
                    "start_time": self.session_start.isoformat() if self.session_start else None,
                    "end_time": datetime.now().isoformat(),
                    "total_transcripts": len(self.transcripts),
                    "total_duration": (datetime.now() - self.session_start).total_seconds() if self.session_start else 0
                },
                "transcripts": self.transcripts
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Transcripts saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save transcripts: {e}")
    
    def export_transcripts(self, format_type: str = "txt"):
        """Export transcripts in different formats."""
        if not self.transcripts:
            print("❌ No transcripts to export.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if format_type.lower() == "txt":
                # Plain text format
                filename = f"transcription_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Transcription Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*60 + "\n\n")
                    
                    for transcript in self.transcripts:
                        time_str = datetime.fromisoformat(transcript["timestamp"].replace('Z', '+00:00')).strftime("%H:%M:%S")
                        f.write(f"[{time_str}] {transcript['text']}\n")
                
                print(f"✅ Text export saved to: {filename}")
                
            elif format_type.lower() == "srt":
                # SRT subtitle format
                filename = f"transcription_{timestamp}.srt"
                with open(filename, 'w', encoding='utf-8') as f:
                    for i, transcript in enumerate(self.transcripts, 1):
                        start_time = transcript["session_time"]
                        end_time = start_time + 3  # Assume 3 second duration per segment
                        
                        def format_srt_time(seconds):
                            hours = int(seconds // 3600)
                            minutes = int((seconds % 3600) // 60)
                            secs = int(seconds % 60)
                            millis = int((seconds % 1) * 1000)
                            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
                        
                        f.write(f"{i}\n")
                        f.write(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n")
                        f.write(f"{transcript['text']}\n\n")
                
                print(f"✅ SRT export saved to: {filename}")
                
            elif format_type.lower() == "csv":
                # CSV format
                import csv
                filename = f"transcription_{timestamp}.csv"
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Session_Time", "Text", "Word_Count"])
                    
                    for transcript in self.transcripts:
                        writer.writerow([
                            transcript["timestamp"],
                            transcript["session_time"],
                            transcript["text"],
                            len(transcript["text"].split())
                        ])
                
                print(f"✅ CSV export saved to: {filename}")
                
            else:
                print(f"❌ Unsupported format: {format_type}")
                print("💡 Available formats: txt, srt, csv")
                
        except Exception as e:
            print(f"❌ Failed to export transcripts: {e}")
    
    async def handle_commands(self):
        """Handle user commands."""
        try:
            while self.transcription_active:
                try:
                    # Get user input
                    command = input("🎤 Command: ").strip().lower()
                    
                    if command in ['quit', 'exit', 'q']:
                        print("👋 Ending transcription session...")
                        self.transcription_active = False
                        break
                    
                    elif command == 'start':
                        if not self.client.recording:
                            self.client.start_recording()
                        else:
                            print("⚠️  Already recording!")
                    
                    elif command == 'stop':
                        if self.client.recording:
                            self.client.stop_recording()
                        else:
                            print("⚠️  Not currently recording!")
                    
                    elif command == 'save':
                        self.save_transcripts()
                    
                    elif command.startswith('export'):
                        parts = command.split()
                        format_type = parts[1] if len(parts) > 1 else "txt"
                        self.export_transcripts(format_type)
                    
                    elif command == 'stats':
                        self.show_stats()
                    
                    elif command == 'clear':
                        self.transcripts.clear()
                        print("🧹 Transcripts cleared!")
                    
                    elif command == 'help':
                        self.print_instructions()
                    
                    else:
                        print(f"❓ Unknown command: {command}")
                        print("💡 Type 'help' for available commands")
                
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            print(f"❌ Command handling error: {e}")
    
    async def run_transcription(self):
        """Run the main transcription loop."""
        try:
            self.transcription_active = True
            self.print_instructions()
            
            print("\n🎉 Transcription session started!")
            print("💡 Type 'start' to begin recording, or 'help' for commands")
            
            # Handle commands
            await self.handle_commands()
            
        except KeyboardInterrupt:
            print("\n⚠️  Transcription interrupted by user")
        except Exception as e:
            print(f"❌ Transcription error: {e}")
        finally:
            self.transcription_active = False
    
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            if self.client.recording:
                self.client.stop_recording()
            self.client.disconnect()
        
        # Auto-save transcripts if any exist
        if self.transcripts:
            print("💾 Auto-saving transcripts...")
            self.save_transcripts()
        
        print("🧹 Cleanup completed")
    
    async def run(self):
        """Run the complete transcription demo."""
        try:
            # Setup
            if not await self.setup():
                return
            
            # Run transcription
            await self.run_transcription()
            
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
    except ImportError as e:
        print(f"❌ Error: Missing required package: {e}")
        print("💡 Install requirements: pip install pyaudio websocket-client")
        return False
    
    return True


async def main():
    """Main function."""
    print("🚀 Starting OpenAI Realtime API Transcription Demo")
    
    # Check requirements
    if not check_requirements():
        return
    
    # Get output file if specified
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create and run demo
    demo = TranscriptionDemo(output_file=output_file)
    await demo.run()
    
    print("👋 Demo completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}") 