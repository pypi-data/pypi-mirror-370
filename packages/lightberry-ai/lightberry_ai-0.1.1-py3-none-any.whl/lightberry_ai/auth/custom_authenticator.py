"""
Custom server authentication module for Lightberry AI SDK

Handles authentication with custom LiveKit servers via their token servers.
"""

import aiohttp
import logging
from typing import Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


async def get_token_from_custom_server(
    livekit_url: str,
    participant_name: str,
    room_name: str = "lightberry"
) -> str:
    """
    Get authentication token from custom LiveKit server's token server.
    
    Converts the LiveKit WebSocket URL to the corresponding token server HTTP URL.
    For example: ws://192.168.1.100:7880 -> http://192.168.1.100:8090/api/token
    
    Args:
        livekit_url: The LiveKit WebSocket URL (e.g., "ws://192.168.1.100:7880")
        participant_name: The participant name (identity)
        room_name: The room name to join (defaults to "lightberry")
    
    Returns:
        Authentication token for the LiveKit server
    
    Raises:
        Exception: If token server is not accessible or returns an error
    """
    # Parse the LiveKit URL to extract host
    parsed = urlparse(livekit_url)
    host = parsed.hostname or "localhost"
    
    # Build token server URL (assumes token server is on port 8090)
    token_server_url = f"http://{host}:8090/api/token"
    
    print(f"  Token server: {token_server_url}")
    logger.info(f"Getting token from custom server at {token_server_url}")
    logger.info(f"Participant: {participant_name}, Room: {room_name}")
    
    payload = {
        "room": room_name,
        "identity": participant_name
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(token_server_url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                
                token = data.get("token")
                if not token:
                    raise Exception("Token server did not return a token")
                
                logger.info(f"Successfully got token from custom server for room: {room_name}")
                return token
                
    except aiohttp.ClientError as e:
        logger.error(f"Failed to connect to custom token server at {token_server_url}: {e}")
        raise Exception(
            f"Could not connect to custom token server at {token_server_url}. "
            f"Please ensure the token server is running on port 8090."
        )
    except Exception as e:
        logger.error(f"Error getting token from custom server: {e}")
        raise