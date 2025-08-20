"""
Example: Override Assistant for Testing

This example demonstrates how to override the configured assistant with a custom one.
⚠️  WARNING: This feature should only be used for testing purposes!

The assistant_name parameter allows you to specify a different assistant than the one
configured for your device. This is useful for testing different assistants without
changing your device configuration.

Note: If multiple assistants with the same name exist on your account, the system will
select the first one found in the lookup.
"""

import asyncio
import os
from dotenv import load_dotenv
from lightberry_ai import LBBasicClient

# Load environment variables
load_dotenv()

async def main():
    # Get credentials from environment
    api_key = os.environ.get("LIGHTBERRY_API_KEY", "your-api-key")
    device_id = os.environ.get("DEVICE_ID", "your-device-id")
    
    # Create client with custom assistant name
    # ⚠️  This will trigger a warning about overriding the assistant
    client = LBBasicClient(
        api_key=api_key,
        device_id=device_id,
        enable_aec=True,
        log_level="INFO",
        assistant_name="Your Test Assistant"  # Override the configured assistant
    )
    
    try:
        # Connect to the service
        print("Connecting with custom assistant...")
        await client.connect()
        
        print(f"Connected to room: {client.room_name}")
        print(f"Participant name: {client.participant_name}")
        print("⚠️  Using overridden assistant: Your Test Assistant")
        
        # Start audio streaming
        print("\nStarting audio streaming...")
        print("Press Ctrl+C to stop")
        
        await client.enable_audio()
        
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    asyncio.run(main())