#!/usr/bin/env python3
"""
Audio Test Script

Simple test to verify that PyAudio can play audio output.
This helps debug audio issues with the OpenAI Realtime API.
"""

import pyaudio
import numpy as np
import time

def test_audio_output():
    """Test PyAudio audio output with a simple tone."""
    print("🔊 Testing PyAudio audio output...")
    
    try:
        # Audio configuration (matching OpenAI Realtime API specs)
        sample_rate = 24000
        channels = 1
        audio_format = pyaudio.paInt16
        chunk_size = 1024
        duration = 2  # seconds
        frequency = 440  # Hz (A4 note)
        
        # Create PyAudio instance
        p = pyaudio.PyAudio()
        
        print(f"📋 Audio Configuration:")
        print(f"   Sample Rate: {sample_rate} Hz")
        print(f"   Channels: {channels}")
        print(f"   Format: {audio_format}")
        print(f"   Chunk Size: {chunk_size}")
        
        # List available audio devices
        print("\n🎛️  Available audio devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:
                print(f"   {i}: {info['name']} (Output)")
        
        # Create output stream
        stream = p.open(
            format=audio_format,
            channels=channels,
            rate=sample_rate,
            output=True,
            frames_per_buffer=chunk_size
        )
        
        print(f"\n🎵 Playing {frequency}Hz tone for {duration} seconds...")
        
        # Generate and play a sine wave
        samples_per_chunk = chunk_size
        total_samples = int(sample_rate * duration)
        
        for i in range(0, total_samples, samples_per_chunk):
            # Generate sine wave samples
            t = np.arange(i, min(i + samples_per_chunk, total_samples)) / sample_rate
            samples = np.sin(2 * np.pi * frequency * t)
            
            # Convert to 16-bit PCM
            audio_data = (samples * 32767).astype(np.int16).tobytes()
            
            # Play the chunk
            stream.write(audio_data)
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        print("✅ Audio test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        return False

def test_microphone_input():
    """Test PyAudio microphone input."""
    print("\n🎤 Testing PyAudio microphone input...")
    
    try:
        # Audio configuration
        sample_rate = 24000
        channels = 1
        audio_format = pyaudio.paInt16
        chunk_size = 1024
        duration = 2  # seconds
        
        # Create PyAudio instance
        p = pyaudio.PyAudio()
        
        # List available input devices
        print("\n🎛️  Available input devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"   {i}: {info['name']} (Input)")
        
        # Create input stream
        stream = p.open(
            format=audio_format,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk_size
        )
        
        print(f"\n🔴 Recording for {duration} seconds... speak now!")
        
        frames = []
        for i in range(0, int(sample_rate / chunk_size * duration)):
            data = stream.read(chunk_size)
            frames.append(data)
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        total_frames = len(frames)
        total_bytes = sum(len(frame) for frame in frames)
        
        print(f"✅ Microphone test completed!")
        print(f"   Recorded {total_frames} frames ({total_bytes} bytes)")
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 PyAudio Compatibility Test")
    print("="*40)
    
    # Test audio output
    output_ok = test_audio_output()
    
    # Test microphone input
    input_ok = test_microphone_input()
    
    print("\n" + "="*40)
    print("📊 Test Results:")
    print(f"   Audio Output: {'✅ PASS' if output_ok else '❌ FAIL'}")
    print(f"   Microphone Input: {'✅ PASS' if input_ok else '❌ FAIL'}")
    
    if output_ok and input_ok:
        print("\n🎉 All audio tests passed! Your system should work with the OpenAI Realtime API.")
    else:
        print("\n⚠️  Some audio tests failed. You may experience issues with the voice agent.")
        print("💡 Troubleshooting tips:")
        print("   - Check that your microphone and speakers are connected")
        print("   - Ensure audio drivers are up to date")
        print("   - Try running as administrator")
        print("   - Check Windows audio permissions")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}") 