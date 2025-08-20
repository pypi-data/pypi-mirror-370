#!/usr/bin/env python3
"""
Tool Client Example

This example demonstrates how to use LightberryToolClient for audio streaming
with tool execution support.

Tools are defined in local_tool_responses.py using the @tool decorator.
"""

import asyncio
import os
import argparse
from dotenv import load_dotenv
from lightberry_ai import LBToolClient

async def main():
    """Tool-enabled audio streaming example."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Tool-enabled audio streaming with Lightberry")
    parser.add_argument("--livekit-url", type=str, help="Custom LiveKit server URL (e.g., ws://192.168.1.100:7880)")
    parser.add_argument("--room", type=str, help="Room name to join")
    parser.add_argument("--device-index", type=int, default=None, help="Audio device index (use list_audio_devices.py to find)")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        print("Error: LIGHTBERRY_API_KEY and DEVICE_ID must be set in .env file")
        return
    
    print("=== Lightberry Tool-Enabled Audio Streaming ===")
    print("[TEST] Print statement is working - edits are being executed!")
    print(f"Device ID: {device_id}")
    
    # Create client with audio configuration
    client = LBToolClient(
        api_key=api_key,
        device_id=device_id,
        device_index=args.device_index,  # Use specified audio device or default
        enable_aec=True,          # Enable echo cancellation
        log_level="WARNING",      # Set logging level
        livekit_url_override=args.livekit_url  # Use custom server if provided
    )
    
    try:
        # Connect to Lightberry service
        if args.livekit_url:
            print(f"\nConnecting to custom server: {args.livekit_url}")
        else:
            print("\nConnecting to Lightberry service...")
        await client.connect(room_name=args.room)
        
        print(f"Connected! Room: {client.room_name}, Participant: {client.participant_name}")
        print(f"Tool channel: {client.data_channel_name}")
        
        # Start audio streaming with tool support
        print("\nStarting audio streaming with tool support...")
        print("Tools from local_tool_responses.py are now available for remote execution")
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
