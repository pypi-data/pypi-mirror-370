#!/usr/bin/env python3
"""
Example of connecting to a custom LiveKit server using URL override.

This example demonstrates how to:
1. Authenticate with the Lightberry API for verification
2. Connect to a custom LiveKit server at a specific IP address
3. Use command-line arguments to specify the server URL

Usage:
    # Connect to custom server with default room "lightberry"
    python custom_server_example.py --livekit-url ws://192.168.1.100:7880
    
    # Connect to custom server with specific room
    python custom_server_example.py --livekit-url ws://192.168.1.100:7880 --room my-room
    
    # Use tool client instead of basic client
    python custom_server_example.py --livekit-url ws://192.168.1.100:7880 --tool-client
"""

import asyncio
import argparse
import logging
import os
from lightberry_ai import LBBasicClient, LBToolClient
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def run_basic_client(livekit_url: str, room_name: str = None):
    """Run the basic audio client with custom server."""
    
    # Load credentials from environment
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        logger.error("Please set LIGHTBERRY_API_KEY and DEVICE_ID environment variables")
        return
    
    logger.info(f"Connecting to custom LiveKit server: {livekit_url}")
    if room_name:
        logger.info(f"Room: {room_name}")
    else:
        logger.info("Room: lightberry (default)")
    
    # Create client with custom LiveKit URL override
    client = LBBasicClient(
        api_key=api_key,
        device_id=device_id,
        livekit_url_override=livekit_url,
        log_level="INFO"
    )
    
    try:
        # Connect to custom server
        # If room_name is not provided, it defaults to "lightberry"
        await client.connect(room_name=room_name)
        
        logger.info(f"Successfully connected!")
        logger.info(f"Room: {client.room_name}")
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
        logger.info("Disconnected")


async def run_tool_client(livekit_url: str, room_name: str = None):
    """Run the tool client with custom server."""
    
    # Load credentials from environment
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        logger.error("Please set LIGHTBERRY_API_KEY and DEVICE_ID environment variables")
        return
    
    logger.info(f"Connecting to custom LiveKit server with tool support: {livekit_url}")
    if room_name:
        logger.info(f"Room: {room_name}")
    else:
        logger.info("Room: lightberry (default)")
    
    # Create tool client with custom LiveKit URL override
    client = LBToolClient(
        api_key=api_key,
        device_id=device_id,
        livekit_url_override=livekit_url,
        log_level="INFO"
    )
    
    try:
        # Connect to custom server
        # If room_name is not provided, it defaults to "lightberry"
        await client.connect(room_name=room_name)
        
        logger.info(f"Successfully connected with tool support!")
        logger.info(f"Room: {client.room_name}")
        logger.info(f"Participant: {client.participant_name}")
        logger.info(f"Tool channel: {client.data_channel_name}")
        
        # Enable audio streaming with tool support
        logger.info("Starting audio with tool support... Press Ctrl+C to stop")
        await client.enable_audio()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await client.disconnect()
        logger.info("Disconnected")


async def main():
    """Main function with command-line argument parsing."""
    
    parser = argparse.ArgumentParser(
        description="Connect to a custom LiveKit server with Lightberry SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Connect to custom server at specific IP
  python custom_server_example.py --livekit-url ws://192.168.1.100:7880
  
  # Connect with specific room name
  python custom_server_example.py --livekit-url ws://192.168.1.100:7880 --room my-room
  
  # Use tool client for tool execution support
  python custom_server_example.py --livekit-url ws://192.168.1.100:7880 --tool-client
  
  # Connect to secure WebSocket server
  python custom_server_example.py --livekit-url wss://my-server.com:7880
        """
    )
    
    parser.add_argument(
        "--livekit-url",
        type=str,
        required=True,
        help="LiveKit server URL (e.g., ws://192.168.1.100:7880)"
    )
    
    parser.add_argument(
        "--room",
        type=str,
        default=None,
        help="Room name to join (default: 'lightberry')"
    )
    
    parser.add_argument(
        "--tool-client",
        action="store_true",
        help="Use tool client instead of basic client"
    )
    
    args = parser.parse_args()
    
    # Validate URL format
    if not args.livekit_url.startswith(("ws://", "wss://")):
        logger.error("LiveKit URL must start with ws:// or wss://")
        return
    
    print("\n" + "=" * 60)
    print("LIGHTBERRY SDK - CUSTOM SERVER CONNECTION")
    print("=" * 60)
    print(f"\nServer: {args.livekit_url}")
    print(f"Room: {args.room or 'lightberry (default)'}")
    print(f"Client type: {'Tool Client' if args.tool_client else 'Basic Client'}")
    print("\nThis will:")
    print("1. Verify your API credentials with Lightberry")
    print("2. Get a token from the custom server's token server")
    print("3. Connect to the custom LiveKit server")
    print("=" * 60 + "\n")
    
    # Run the appropriate client
    if args.tool_client:
        await run_tool_client(args.livekit_url, args.room)
    else:
        await run_basic_client(args.livekit_url, args.room)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")