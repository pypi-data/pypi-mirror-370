"""
Local authentication module for Lightberry AI SDK

Handles authentication with local LiveKit server via token server.
"""

import aiohttp
import logging
from typing import Optional, Tuple

# Local server configuration
LOCAL_TOKEN_SERVER_URL = "http://localhost:8090/api/token"
LOCAL_LIVEKIT_URL = "ws://localhost:7880"

logger = logging.getLogger(__name__)


async def authenticate_local(
    participant_name: str,
    room_name: str,
    assistant_name: Optional[str] = None,  # Ignored in local mode
    has_initial_transcripts: bool = False,  # Ignored in local mode
    session_instructions: Optional[str] = None  # Ignored in local mode
) -> Tuple[str, str, str]:
    """
    Authenticate with local LiveKit token server.
    
    Args:
        participant_name: The participant name (identity)
        room_name: The room name to join
        assistant_name: Ignored in local mode (server configuration handled separately)
        has_initial_transcripts: Ignored in local mode
        session_instructions: Ignored in local mode
    
    Returns:
        Tuple of (token, room_name, livekit_url)
    
    Raises:
        Exception: If authentication fails or token server is not running
    """
    if assistant_name:
        logger.info(f"Note: assistant_name '{assistant_name}' is ignored in local mode")
    
    logger.info(f"Authenticating with local token server for participant: {participant_name}, room: {room_name}")
    
    payload = {
        "room": room_name,
        "identity": participant_name
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(LOCAL_TOKEN_SERVER_URL, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                
                token = data.get("token")
                if not token:
                    raise Exception("Token server did not return a token")
                
                logger.info(f"Successfully authenticated with local server for room: {room_name}")
                return token, room_name, LOCAL_LIVEKIT_URL
                
    except aiohttp.ClientError as e:
        logger.error(f"Failed to connect to local token server at {LOCAL_TOKEN_SERVER_URL}: {e}")
        raise Exception(
            f"Could not connect to local token server. "
            f"Please ensure the local LiveKit server is running. "
            f"Run './start-all.sh' in the local-livekit directory."
        )
    except Exception as e:
        logger.error(f"Error during local authentication: {e}")
        raise