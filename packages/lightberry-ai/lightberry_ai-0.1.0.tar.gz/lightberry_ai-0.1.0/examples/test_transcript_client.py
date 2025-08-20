#!/usr/bin/env python3
"""
Test Transcript Client

A minimal client script specifically designed for automated testing of transcript features.
Supports loading initial transcripts from the INITIAL_TRANSCRIPTS environment variable.

This script is intended for use by the test automation framework and provides a simple
interface for testing transcript initialization functionality.
"""

import asyncio
import os
import json
from dotenv import load_dotenv
from lightberry_ai import LBBasicClient

async def main():
    """Test transcript client with environment variable support."""
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        print("Error: LIGHTBERRY_API_KEY and DEVICE_ID must be set in .env file")
        return
    
    # Check for initial transcripts from environment (for testing)
    initial_transcripts = None
    initial_transcripts_json = os.getenv("INITIAL_TRANSCRIPTS")
    if initial_transcripts_json:
        try:
            initial_transcripts = json.loads(initial_transcripts_json)
            print(f"📝 Loaded {len(initial_transcripts)} initial transcripts from environment")
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing INITIAL_TRANSCRIPTS: {e}")
            return
    
    print("=== Lightberry Test Transcript Client ===")
    print(f"Device ID: {device_id}")
    if initial_transcripts:
        print(f"Initial Transcripts: {len(initial_transcripts)} messages")
    else:
        print("Initial Transcripts: None (normal welcome flow)")
    
    # Create client with audio configuration
    client = LBBasicClient(
        api_key=api_key,
        device_id=device_id,
        device_index=None,        # Use default audio device
        enable_aec=True,          # Enable echo cancellation
        log_level="INFO",         # More verbose for testing
        initial_transcripts=initial_transcripts  # Pass initial transcripts if provided
    )
    
    try:
        # Connect to Lightberry service
        print("\nConnecting to Lightberry service...")
        await client.connect()
        
        print(f"Connected! Room: {client.room_name}, Participant: {client.participant_name}")
        
        # Start audio streaming
        print("\nStarting audio streaming...")
        if initial_transcripts:
            print("Expected: Conversation should continue from transcript history")
            print("Expected: No welcome greeting should occur")
        else:
            print("Expected: Normal welcome greeting should occur")
        
        await client.enable_audio()
        
    except KeyboardInterrupt:
        print("\nStopping test client...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()
        print("Test client disconnected.")

if __name__ == "__main__":
    asyncio.run(main())