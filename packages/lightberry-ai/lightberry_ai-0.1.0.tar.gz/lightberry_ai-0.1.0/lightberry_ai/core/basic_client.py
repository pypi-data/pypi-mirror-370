"""
LightberryBasicClient - Audio-only streaming client

This client provides audio-only streaming functionality using LiveKit infrastructure.
Audio is processed at 48kHz sample rate with optional echo cancellation.
"""

import logging
import os
from typing import Optional
from dotenv import load_dotenv

# Import the SDK's audio streaming functionality
from .audio_streaming import main as audio_main
from ..auth import authenticate, authenticate_local, get_token_from_custom_server

load_dotenv()

logger = logging.getLogger(__name__)


class LBBasicClient:
    """
    Basic audio streaming client for LiveKit.
    
    Provides audio-only streaming with configurable echo cancellation and device selection.
    Audio processing uses 48kHz sample rate with mono channel configuration.
    
    Args:
        api_key: Lightberry API key for authentication (optional for local mode)
        device_id: Device identifier for multi-device client management (optional for local mode)
        use_local: Use local LiveKit server instead of cloud (default: False)
        device_index: Audio device index (None for system default)
        enable_aec: Enable acoustic echo cancellation (default: True)
        log_level: Logging verbosity level (DEBUG, INFO, WARNING, ERROR)
        assistant_name: Optional assistant name to override configured assistant (testing only)
        initial_transcripts: Optional list of transcript dictionaries to initialize conversation history
        session_instructions: Optional instructions to append to the system prompt for this session only
        livekit_url_override: Optional custom LiveKit server URL (e.g., "ws://192.168.1.100:7880")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        device_id: Optional[str] = None,
        use_local: bool = False,
        device_index: Optional[int] = None,
        enable_aec: bool = True,
        log_level: str = "WARNING",
        assistant_name: Optional[str] = None,
        initial_transcripts: Optional[list] = None,
        session_instructions: Optional[str] = None,
        livekit_url_override: Optional[str] = None
    ):
        # Validate required parameters based on mode
        if not use_local and not livekit_url_override and (not api_key or not device_id):
            raise ValueError("api_key and device_id are required for remote mode")
        
        self.api_key = api_key
        self.device_id = device_id if device_id else "local-device"
        self.use_local = use_local
        self.device_index = device_index
        self.enable_aec = enable_aec
        self.log_level = log_level
        self.assistant_name = assistant_name
        self.initial_transcripts = initial_transcripts
        self.session_instructions = session_instructions
        self.livekit_url_override = livekit_url_override
        
        # Set by authentication
        self._participant_name: Optional[str] = None
        self._room_name: Optional[str] = None
        self._token: Optional[str] = None
        self._livekit_url: Optional[str] = None
        
        # Configure logging
        logging.basicConfig(level=getattr(logging, log_level.upper()))
        logger.info(f"LBBasicClient initialized with AEC: {enable_aec}")
        
    async def connect(self, room_name: Optional[str] = None) -> None:
        """
        Connect to LiveKit room.
        
        For remote mode: Authenticates using API key and device ID.
        For local mode: Connects to local LiveKit server.
        For custom override: Authenticates with API, then connects to custom server.
        
        Args:
            room_name: Room name (defaults to "lightberry" when using custom override)
        
        Raises:
            Exception: If quota is exceeded, displays "Quota reached." message
            Exception: If authentication fails for other reasons
        """
        # Always generate participant name from device_id with @device_id suffix
        participant_name = f"sdk-user-{self.device_id}@{self.device_id}"
        
        if self.use_local:
            logger.info("Connecting to local LiveKit server...")
            
            # Use provided room name or default to "lightberry"
            if not room_name:
                room_name = "lightberry"
                
            # Use local authentication
            auth_func = authenticate_local
        else:
            logger.info("Connecting to Lightberry service...")
            
            # For remote mode, room name comes from environment or default
            if not self.livekit_url_override:
                room_name = os.environ.get("ROOM_NAME", "lightberry")
            
            # Use remote authentication
            auth_func = authenticate
        
        try:
            # If using custom override, we still authenticate with API first
            if self.livekit_url_override and not self.use_local:
                # Step 1: Authenticate with Lightberry API to verify credentials
                print(f"\n🔌 Connecting to custom LiveKit server: {self.livekit_url_override}")
                print("Step 1: Verifying credentials with Lightberry API...")
                logger.info("Verifying credentials with Lightberry API...")
                has_initial_transcripts = self.initial_transcripts is not None
                
                # Use dummy room name for API verification
                api_token, api_room, api_url = await auth_func(
                    participant_name,
                    "verification",
                    self.assistant_name,
                    has_initial_transcripts=has_initial_transcripts,
                    session_instructions=self.session_instructions
                )
                
                logger.info("API credentials verified successfully")
                print("✅ API credentials verified")
                
                # Step 2: Use custom server with default room "lightberry" if not specified
                room_name = room_name or "lightberry"
                print(f"Step 2: Getting token from custom server...")
                print(f"  Server: {self.livekit_url_override}")
                print(f"  Room: {room_name}")
                logger.info(f"Getting token for custom server: {self.livekit_url_override}")
                
                # Step 3: Get token from custom server
                custom_token = await get_token_from_custom_server(
                    self.livekit_url_override,
                    participant_name,
                    room_name
                )
                
                # Use custom values
                self._participant_name = participant_name
                self._room_name = room_name
                self._token = custom_token
                self._livekit_url = self.livekit_url_override
                
                print(f"✅ Ready to connect!")
                print(f"  Final URL: {self.livekit_url_override}")
                print(f"  Room: {room_name}")
                print(f"  Participant: {participant_name}\n")
                logger.info(f"Ready to connect to custom server - Room: {room_name}, URL: {self.livekit_url_override}")
            else:
                # Normal flow for local or remote mode
                has_initial_transcripts = self.initial_transcripts is not None
                
                token, room_name, livekit_url = await auth_func(
                    participant_name, 
                    room_name, 
                    self.assistant_name,
                    has_initial_transcripts=has_initial_transcripts,
                    session_instructions=self.session_instructions
                )
                
                self._participant_name = participant_name
                self._room_name = room_name
                self._token = token
                self._livekit_url = livekit_url
                
                logger.info(f"Successfully authenticated - Room: {room_name}, Participant: {participant_name}")
            
        except Exception as e:
            # Check for quota exceeded (when server side is implemented)
            if "quota" in str(e).lower():
                raise Exception("Quota reached.")
            else:
                raise e
    
    async def enable_audio(self) -> None:
        """
        Enable bidirectional audio streaming.
        
        Begins audio streaming using the authenticated connection and sets up
        the hardware output device. This method will run until manually stopped
        or interrupted.
        
        Raises:
            RuntimeError: If called before connect()
        """
        if not self._participant_name:
            raise RuntimeError("Must call connect() before enable_audio()")
            
        logger.info("Starting audio streaming...")
        
        # Call the existing main function with our parameters and the token
        await audio_main(
            participant_name=self._participant_name,
            enable_aec=self.enable_aec,
            initial_transcripts=self.initial_transcripts,
            token=self._token,
            livekit_url=self._livekit_url
        )
    
    async def disconnect(self) -> None:
        """
        Disconnect from the LiveKit room.
        
        Performs cleanup and disconnects from the LiveKit room.
        """
        logger.info("Disconnecting from Lightberry service...")
        # The main function handles its own cleanup
        self._participant_name = None
        self._room_name = None
        self._token = None
        self._livekit_url = None
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected and ready for streaming."""
        return self._participant_name is not None
    
    @property
    def participant_name(self) -> Optional[str]:
        """Get the participant name assigned by authentication."""
        return self._participant_name
    
    @property
    def room_name(self) -> Optional[str]:
        """Get the room name assigned by authentication."""
        return self._room_name
    
    @property
    def livekit_url(self) -> Optional[str]:
        """Get the LiveKit server URL being used."""
        return self._livekit_url