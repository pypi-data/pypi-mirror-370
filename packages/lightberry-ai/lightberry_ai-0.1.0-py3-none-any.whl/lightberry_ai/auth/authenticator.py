"""
Authentication module for Lightberry AI SDK

Handles authentication with Lightberry API service and fallback to local token generation.
"""

import os
import json
import aiohttp
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get LiveKit credentials from environment variables
DEVICE_ID = os.environ.get("DEVICE_ID")
LIGHTBERRY_API_KEY = os.environ.get("LIGHTBERRY_API_KEY")

# Default LiveKit URL fallback
DEFAULT_LIVEKIT_URL = "wss://lb-ub8o0q4v.livekit.cloud"

# Auth API configuration
AUTH_API_URL = os.environ.get("AUTH_API_URL", "https://dashboard.lightberry.com/api/authenticate/{}")

logger = logging.getLogger(__name__)





async def get_credentials_from_api(participant_name: str, assistant_name: Optional[str] = None, has_initial_transcripts: bool = False, session_instructions: Optional[str] = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Fetches LiveKit token, room name, and URL from the authentication API.
    
    Args:
        participant_name: The participant name (username)
        assistant_name: Optional assistant name to override configured assistant (testing only).
                       If multiple assistants with the same name exist, the first one found will be used.
        has_initial_transcripts: Whether the client has initial transcripts to send
        session_instructions: Optional instructions to append to the system prompt for this session only
    
    Returns:
        Tuple of (token, room_name, livekit_url) or (None, None, None) if failed
    """
    if not DEVICE_ID:
        logger.error("DEVICE_ID not set in environment variables")
        return None, None, None
    
    url = AUTH_API_URL.format(DEVICE_ID)
    
    # TODO: Add LIGHTBERRY_API_KEY to payload when server side is ready
    # Current payload format maintained for compatibility
    api_key = LIGHTBERRY_API_KEY  # Reference API key for future use
    payload = {"username": participant_name, "x-device-api-key": api_key}
    if assistant_name:
        payload["assistant_name"] = assistant_name
        logger.warning("⚠️  WARNING: Manually overwriting the assistant to a different one than is configured. Use this only for testing.")
    if has_initial_transcripts:
        payload["has_initial_transcripts"] = True
        logger.info("📝 Client has initial transcripts to send")
    if session_instructions:
        payload["session_instructions"] = session_instructions
        logger.info("📋 Client has session instructions to send")
    logger.info(f"Attempting to fetch credentials from {url} for username '{participant_name}', device_id '{DEVICE_ID}'{', assistant: ' + assistant_name if assistant_name else ''}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                
                if data.get("success"):
                    token = data.get("livekit_token")
                    room_name = data.get("room_name")
                    livekit_url = data.get("livekit_url", DEFAULT_LIVEKIT_URL)  # Use fallback if not provided
                    
                    if token and room_name:
                        logger.info(f"Successfully retrieved credentials: {room_name}, URL: {livekit_url}")
                        return token, room_name, livekit_url
                    else:
                        logger.error("API response missing token or room name.")
                        return None, None, None
                else:
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"API request failed: {error_msg}")
                    return None, None, None
    except Exception as e:
        logger.error(f"Error fetching credentials from API: {e}")
        return None, None, None


async def authenticate(participant_name: str, fallback_room_name: str, assistant_name: Optional[str] = None, has_initial_transcripts: bool = False, session_instructions: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Unified authentication function that tries remote API first, then falls back to local token generation.
    
    Args:
        participant_name: The participant name (username)
        fallback_room_name: Room name to use if API fails
        assistant_name: Optional assistant name to override configured assistant (testing only).
                       If multiple assistants with the same name exist, the first one found will be used.
        has_initial_transcripts: Whether the client has initial transcripts to send
        session_instructions: Optional instructions to append to the system prompt for this session only
    
    Returns:
        Tuple of (token, room_name, livekit_url)
    """
    # Try to get credentials from auth API first
    api_token, api_room_name, api_url = await get_credentials_from_api(participant_name, assistant_name, has_initial_transcripts, session_instructions)
    
    if api_token and api_room_name:
        logger.info(f"Using auth API credentials for room: {api_room_name}")
        return api_token, api_room_name, api_url or DEFAULT_LIVEKIT_URL
    else:
        raise Exception("Authentication via API failed, please check your device ID and API key")
        
