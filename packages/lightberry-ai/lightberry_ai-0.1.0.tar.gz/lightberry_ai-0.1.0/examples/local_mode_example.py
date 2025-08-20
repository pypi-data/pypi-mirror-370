#!/usr/bin/env python3
"""
Example of using Lightberry SDK with local LiveKit server.

This example demonstrates how to connect to a local LiveKit server
instead of the cloud service. Perfect for development and testing.

Prerequisites:
1. Start the local LiveKit server:
   cd ../local-livekit
   ./start-all.sh

2. Run this example:
   python local_mode_example.py
"""

import asyncio
import logging
import os
from lightberry_ai import LBBasicClient, LBToolClient
from dotenv import load_dotenv

load_dotenv()

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_local_basic_client():
    """Test the basic audio client with local server."""
    logger.info("=" * 50)
    logger.info("Testing LBBasicClient with local server")
    logger.info("=" * 50)
    
    # Load device ID from environment (optional for local mode, but provides consistent participant naming)
    device_id = os.getenv("DEVICE_ID", "local-test-device")
    
    # Create client for local mode - API key not needed, but device_id gives better participant names
    client = LBBasicClient(use_local=True, device_id=device_id, log_level="WARNING")
    
    try:
        # Connect to local server - defaults to "lightberry" room
        await client.connect()
        
        logger.info(f"Connected to room: {client.room_name}")
        logger.info(f"Participant: {client.participant_name}")
        
        # Enable audio streaming
        logger.info("Starting audio stream... Press Ctrl+C to stop")
        await client.enable_audio()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await client.disconnect()
        logger.info("Disconnected from local server")


async def test_local_tool_client():
    """Test the tool client with local server."""
    logger.info("=" * 50)
    logger.info("Testing LBToolClient with local server")
    logger.info("=" * 50)
    
    # Load device ID from environment for consistent participant naming
    device_id = os.getenv("DEVICE_ID", "local-test-device")
    
    # Create tool client for local mode with device ID
    client = LBToolClient(use_local=True, device_id=device_id, log_level="WARNING")
    
    try:
        # Connect to local server - defaults to "lightberry" room
        # To connect to echo bot room use: await client.connect(room_name="echo-test")
        await client.connect()
        
        logger.info(f"Connected to room: {client.room_name}")
        logger.info(f"Participant: {client.participant_name}")
        
        # Enable audio with tool support
        logger.info("Starting audio with tool support... Press Ctrl+C to stop")
        await client.enable_audio()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await client.disconnect()
        logger.info("Disconnected from local server")


async def compare_local_vs_remote():
    """Example showing how the same code works for both local and remote."""
    logger.info("=" * 50)
    logger.info("Demonstrating local vs remote with same code")
    logger.info("=" * 50)
    
    # This function works with both local and remote modes
    async def run_client(use_local: bool):
        mode = "LOCAL" if use_local else "REMOTE"
        logger.info(f"\n--- Running in {mode} mode ---")
        
        # Load environment variables for both modes
        api_key = os.getenv("LIGHTBERRY_API_KEY", "your_api_key_here")
        device_id = os.getenv("DEVICE_ID", "local-test-device")
        
        if use_local:
            # Local mode - API key not needed, but device_id provides consistent naming
            client = LBBasicClient(use_local=True, device_id=device_id)
        else:
            # Remote mode - requires both API key and device ID
            client = LBBasicClient(
                api_key=api_key,
                device_id=device_id
            )
        
        try:
            # The connect call is almost identical!
            if use_local:
                await client.connect(room_name="echo-test")  # Connect to echo bot room
            else:
                await client.connect()  # Remote mode gets room from API
                
            logger.info(f"{mode}: Connected to {client.room_name}")
            
            # In a real app, you'd run enable_audio here
            # await client.enable_audio()
            
        finally:
            await client.disconnect()
            logger.info(f"{mode}: Disconnected")
    
    # Run local mode example
    await run_client(use_local=True)
    
    # Uncomment to test remote mode (requires valid credentials)
    # await run_client(use_local=False)


async def main():
    """Main function to run examples."""
    print("\n" + "=" * 60)
    print("LIGHTBERRY SDK - LOCAL MODE EXAMPLES")
    print("=" * 60)
    print("\nMake sure the local LiveKit server is running!")
    print("Run './start-all.sh' in the local-livekit directory\n")
    
    # Show device ID being used
    device_id = os.getenv("DEVICE_ID", "local-test-device")
    print(f"Device ID: {device_id}")
    print(f"Participant name will be: sdk-user-{device_id}\n")
    
    print("Select an example to run:")
    print("1. Basic Audio Client (local mode)")
    print("2. Tool Client (local mode)")
    print("3. Compare local vs remote code")
    print("q. Quit")
    print("Using basic client")
    
    #choice = input("\nEnter your choice (1-3 or q): ").strip()
    choice = "1"    #hardcode to basic client for now for testing

    if choice == "1":
        await test_local_basic_client()
    elif choice == "2":
        await test_local_tool_client()
    elif choice == "3":
        await compare_local_vs_remote()
    elif choice.lower() == "q":
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
