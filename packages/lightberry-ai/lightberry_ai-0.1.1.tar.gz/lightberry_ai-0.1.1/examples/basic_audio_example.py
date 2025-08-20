#!/usr/bin/env python3
"""
Basic Audio Streaming Example

This example demonstrates how to use LightberryBasicClient for audio-only streaming.
"""

import asyncio
import os
from dotenv import load_dotenv
from lightberry_ai import LBBasicClient

async def main():
    """Basic audio streaming example."""
    
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
    
    # Create client with audio configuration
    client = LBBasicClient(
        api_key=api_key,
        device_id=device_id,
        device_index=None,        # Use default audio device
        enable_aec=True,          # Enable echo cancellation
        log_level="WARNING"       # Set logging level
    )
    
    try:
        # Connect to Lightberry service
        print("\nConnecting to Lightberry service...")
        await client.connect()
        
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