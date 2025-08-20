#!/usr/bin/env python3
"""
Basic Audio Streaming Example with Command-Line Arguments

This example demonstrates how to use LightberryBasicClient for audio-only streaming
with support for custom LiveKit server connections.

Usage:
    # Normal connection to Lightberry cloud
    python basic_audio_with_args.py
    
    # Connect to custom LiveKit server
    python basic_audio_with_args.py --livekit-url ws://192.168.1.100:7880
    
    # Connect to custom server with specific room
    python basic_audio_with_args.py --livekit-url ws://192.168.1.100:7880 --room my-room
"""

import asyncio
import argparse
import os
from dotenv import load_dotenv
from lightberry_ai import LBBasicClient

async def main():
    """Basic audio streaming example with command-line arguments."""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Lightberry Basic Audio Streaming with optional custom server",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--livekit-url",
        type=str,
        default=None,
        help="Custom LiveKit server URL (e.g., ws://192.168.1.100:7880)"
    )
    
    parser.add_argument(
        "--room",
        type=str,
        default=None,
        help="Room name to join (default: 'lightberry' for custom servers)"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        print("Error: LIGHTBERRY_API_KEY and DEVICE_ID must be set in .env file")
        return
    
    print("=== Lightberry Basic Audio Streaming ===")
    print(f"Device ID: {device_id}")
    print(f"API Key: {api_key[:8]}..." if api_key else "Not set")
    
    if args.livekit_url:
        print(f"Custom Server: {args.livekit_url}")
        print(f"Room: {args.room or 'lightberry (default)'}")
    else:
        print("Using Lightberry Cloud Service")
    
    # Create client with audio configuration
    client = LBBasicClient(
        api_key=api_key,
        device_id=device_id,
        device_index=None,        # Use default audio device
        enable_aec=True,          # Enable echo cancellation
        log_level="WARNING",      # Set logging level
        livekit_url_override=args.livekit_url  # Custom server URL if provided
    )
    
    try:
        # Connect to Lightberry service or custom server
        print("\nConnecting...")
        await client.connect(room_name=args.room)
        
        print(f"Connected! Room: {client.room_name}, Participant: {client.participant_name}")
        
        # Start audio streaming
        print("\nStarting audio streaming...")
        print("Press Ctrl+C to stop\n")
        
        await client.enable_audio()
        
    except KeyboardInterrupt:
        print("\nStopping audio streaming...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()
        print("Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())