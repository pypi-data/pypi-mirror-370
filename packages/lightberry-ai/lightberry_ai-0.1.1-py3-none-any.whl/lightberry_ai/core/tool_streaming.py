#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "livekit",
#   "livekit-api",
#   "sounddevice",
#   "python-dotenv",
#   "asyncio",
#   "numpy",
#   "aiohttp",
# ]
# ///
"""
Modified audio streaming client with tool call support via LiveKit data channel.

This version adds:
- Data channel support for receiving tool calls
- Integration with LightberryToolServer
- Sending tool execution results back via data channel
"""

import os
import logging
import asyncio
import json
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from livekit import rtc
from ..tools.server import LightberryToolServer  
from ..auth import authenticate, authenticate_local
from . import audio_streaming as stream_audio

# Try to import local_tool_responses to set up app controller if available
try:
    import local_tool_responses
except ImportError:
    local_tool_responses = None

load_dotenv()

logger = logging.getLogger(__name__)


class AppController:
    """Controller to allow tools to control the application."""
    
    def __init__(self):
        self.disconnect_requested = False
        
    def request_disconnect(self):
        """Request the application to disconnect from the room."""
        self.disconnect_requested = True
        logger.info("Disconnect requested by tool")


class AudioStreamWithTools(stream_audio.AudioStreamer):
    """Extended AudioStreamer with data channel support for tool calls."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool_server: Optional[LightberryToolServer] = None
        self.rpc_method_name: str = "tool_call"
        self.tool_channel_name: Optional[str] = None
        self.last_meter_log = 0  # Track last meter log time
        
    def set_tool_server(self, tool_server: LightberryToolServer):
        """Set the tool server instance."""
        self.tool_server = tool_server
        logger.info("Tool server connected to audio streamer")
        
    def set_tool_channel_name(self, name: str):
        """Set the tool channel name to use."""
        self.tool_channel_name = name
        if self.tool_server:
            self.tool_server.set_tool_channel_name(name)
        logger.info(f"Tool channel name set to: {name}")
    
    def should_use_terminal_meter(self):
        """Check if we should use terminal meter based on current log level."""
        # Get the effective logging level for our logger
        effective_level = logger.getEffectiveLevel()
        # Use terminal meter for WARNING (30) and ERROR (40) levels
        return effective_level >= logging.WARNING
    
    def print_audio_meter_adaptive(self):
        """Audio meter that adapts based on logging level."""
        if self.should_use_terminal_meter():
            # Use real-time terminal meter for WARNING/ERROR levels
            self.print_audio_meter_terminal()
        else:
            # Use logging-friendly meter for INFO/DEBUG levels
            self.print_audio_meter_logging()
    
    def print_audio_meter_logging(self):
        """Audio meter display that uses logging instead of terminal output."""
        import time
        
        # Only log every 2 seconds to avoid spam
        current_time = time.time()
        if current_time - self.last_meter_log < 2.0:
            return
        self.last_meter_log = current_time
        
        if not self.meter_running:
            return
            
        # Get local audio level
        local_db = self.micro_db
        local_status = "🔴 MUTED" if self.is_muted else "🎤 LIVE"
        
        # Create a simple text meter for local audio
        if local_db > stream_audio.INPUT_DB_MIN:
            meter_width = 20
            normalized = (local_db - stream_audio.INPUT_DB_MIN) / (stream_audio.INPUT_DB_MAX - stream_audio.INPUT_DB_MIN)
            fill_width = int(normalized * meter_width)
            meter_bar = "█" * fill_width + "░" * (meter_width - fill_width)
            local_text = f"{local_status} [{meter_bar}] {local_db:.1f}dB"
        else:
            local_text = f"{local_status} [{'░' * 20}] {local_db:.1f}dB"
        
        # Get remote participants info
        participants_info = []
        with self.participants_lock:
            for sid, info in self.participants.items():
                if current_time - info['last_update'] < 5.0:  # Only show recent participants
                    participants_info.append(f"{info['name']}: {info['db_level']:.1f}dB")
        
        # Log the meter information
        if participants_info:
            remote_text = " | ".join(participants_info)
            logger.info(f"Audio Levels - Local: {local_text} | Remote: {remote_text}")
        else:
            logger.info(f"Audio Levels - Local: {local_text} | Remote: (no active participants)")
    
    def print_audio_meter_terminal(self):
        """Real-time terminal meter display (like original stream_audio.py)."""
        if not self.meter_running:
            return
        
        # Use the parent class's terminal meter functionality
        # This will use escape sequences for real-time updates
        super().print_audio_meter()


async def main_with_tools(
    participant_name: str = "python-user",
    device_index: Optional[int] = None,
    enable_aec: bool = True,
    data_channel_name: Optional[str] = None,
    initial_transcripts: Optional[list] = None,
    token: Optional[str] = None,
    livekit_url: Optional[str] = None,
    use_local: bool = False
):
    """
    Main function with tool support via data channel.
    
    Args:
        participant_name: Name of the participant
        device_index: Audio device index to use
        enable_aec: Whether to enable echo cancellation
        data_channel_name: Name of the data channel for tool calls
    """
    # Create app controller for tool-based application control
    app_controller = AppController()
    if local_tool_responses:
        local_tool_responses.set_app_controller(app_controller)
    
    # Create extended audio streamer with modified AEC settings for better voice pickup
    streamer = AudioStreamWithTools(enable_aec=enable_aec)
    
    # If AEC is enabled, try less aggressive settings for better voice pickup
    if enable_aec and streamer.audio_processor:
        logger.info("Using standard AEC configuration")
    
    # Create and configure tool server
    tool_server = LightberryToolServer(data_channel_name)
    streamer.set_tool_server(tool_server)
    
    if data_channel_name:
        streamer.set_tool_channel_name(data_channel_name)
    
    # Store the event loop reference
    streamer.loop = asyncio.get_running_loop()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('lightberry_audio_tools.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info(f"Starting audio streaming with tools support")
    logger.info(f"Participant name: {participant_name}")
    logger.info(f"Device index: {device_index}")
    logger.info(f"Echo cancellation: {enable_aec}")
    logger.info(f"Data channel: {data_channel_name}")
    
    # Create LiveKit room
    room = rtc.Room()
    
    # Define RPC handler function (will be registered after connection)
    async def handle_tool_call(rpc_data):
        """Handle tool call via RPC."""
        try:
            # Parse the tool call to extract name and args for printing
            try:
                tool_call = json.loads(rpc_data.payload)
                tool_name = tool_call.get("name", "unknown")
                # Remove 'name' field to show just the arguments
                args = tool_call.copy()
                args.pop("name", None)
                print(f"Tool call received: name: {tool_name} args: {args}")
            except:
                print(f"Tool call received: name: unknown args: {rpc_data.payload}")
            
            if streamer.tool_server:
                # Process the tool call
                response = await streamer.tool_server.process_tool_call(rpc_data.payload)
                return json.dumps(response)
            else:
                logger.warning("Tool server not configured, ignoring tool call")
                return json.dumps({"error": "Tool server not available"})
                
        except Exception as e:
            logger.error(f"Error handling tool call: {e}")
            return json.dumps({"error": str(e)})
    
    # Define data channel handler for tool calls
    def handle_data_channel_message(data: bytes, topic: str):
        """Handle data channel messages."""
        try:
            if topic == "tool_calls":
                # Decode the JSON data
                message = data.decode('utf-8')
                tool_data = json.loads(message)
                
                # Extract tool information for printing
                tool_name = tool_data.get("tool", "unknown")
                arguments = tool_data.get("arguments", {})
                status = tool_data.get("status", "unknown")
                
                print(f"Tool call received: name: {tool_name} args: {arguments} status: {status}")
                
                # Process the tool call if it's in executing status
                if status == "executing" and streamer.tool_server:
                    # Track processed calls to avoid duplicates
                    if not hasattr(streamer, 'processed_calls'):
                        streamer.processed_calls = set()
                    
                    # Create a unique call ID from tool name and timestamp
                    call_id = f"{tool_name}_{time.time()}"
                    
                    # Check if we've recently processed this tool
                    recent_calls = [c for c in streamer.processed_calls if c.startswith(tool_name)]
                    if recent_calls:
                        # Check if any recent call was within 1 second
                        for recent in recent_calls:
                            try:
                                _, timestamp = recent.rsplit('_', 1)
                                if time.time() - float(timestamp) < 1.0:
                                    print(f"⚠️ Ignoring duplicate {tool_name} call within 1 second")
                                    continue
                            except:
                                pass
                    
                    streamer.processed_calls.add(call_id)
                    
                    # Convert to the format expected by our tool server
                    tool_call_payload = {
                        "name": tool_name,
                        **arguments
                    }
                    
                    # Process in background WITHOUT blocking audio processing
                    async def process_async():
                        try:
                            response = await streamer.tool_server.process_tool_call(json.dumps(tool_call_payload))
                            logger.info(f"Tool call processed: {response}")
                        except Exception as e:
                            logger.error(f"Error processing tool call: {e}")
                    
                    # Fire and forget - don't block on tool execution
                    asyncio.create_task(process_async())
                    print(f"✓ Tool {tool_name} execution started (non-blocking)")
                
                elif status == "completed":
                    print(f"✓ Tool call {tool_name} marked as completed by agent")
                        
            else:
                logger.debug(f"Received data on channel '{topic}': {data.decode('utf-8')}")
                
        except Exception as e:
            logger.error(f"Error handling data channel message: {e}")
            logger.error(f"Topic: {topic}, Data: {data}")
    
    # Copy event handlers from original stream_audio
    @room.on("track_published")
    def on_track_published(publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
        logger.info("track published: %s from %s", publication.sid, participant.identity)

    @room.on("track_unpublished")
    def on_track_unpublished(publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
        logger.info("track unpublished: %s from %s", publication.sid, participant.identity)

    @room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant
    ):
        logger.info("track subscribed: %s from %s", publication.sid, participant.identity)
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            audio_stream = rtc.AudioStream(track)
            asyncio.create_task(process_audio_stream(audio_stream, participant))

    @room.on("track_unsubscribed")
    def on_track_unsubscribed(
        track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant
    ):
        logger.info("track unsubscribed: %s from %s", publication.sid, participant.identity)

    @room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logger.info("participant connected: %s %s", participant.sid, participant.identity)
        with streamer.participants_lock:
            streamer.participants[participant.sid] = {
                'name': participant.identity or f"User_{participant.sid[:8]}",
                'db_level': stream_audio.INPUT_DB_MIN,
                'last_update': stream_audio.time.time()
            }

    @room.on("participant_disconnected")
    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        logger.info("participant disconnected: %s %s", participant.sid, participant.identity)
        with streamer.participants_lock:
            if participant.sid in streamer.participants:
                del streamer.participants[participant.sid]

    @room.on("connected")
    def on_connected():
        logger.info("Successfully connected to LiveKit room")
        # Send initial transcripts if provided
        if initial_transcripts:
            async def send_transcripts():
                try:
                    transcript_message = {
                        "type": "initial_transcripts",
                        "transcripts": initial_transcripts
                    }
                    await room.local_participant.publish_data(
                        json.dumps(transcript_message).encode(),
                        topic="initialization"
                    )
                    logger.info(f"📝 Sent {len(initial_transcripts)} initial transcripts to server")
                except Exception as e:
                    logger.error(f"Failed to send initial transcripts: {e}")
            asyncio.create_task(send_transcripts())

    @room.on("disconnected")
    def on_disconnected(reason):
        logger.info(f"Disconnected from LiveKit room: {reason}")
    
    @room.on("data_received")
    def on_data_received(data_packet):
        print(f"[DEBUG] DATA RECEIVED! Topic: {data_packet.topic}, Size: {len(data_packet.data)} bytes")
        try:
            data = data_packet.data
            topic = data_packet.topic
            participant = data_packet.participant
            
            print(f"[DEBUG] Processing data from {participant.identity} on topic '{topic}'")
            
            # Handle transcript streaming
            if topic == "transcripts":
                print(f"[DEBUG] TRANSCRIPT TOPIC DETECTED!")
                transcript = json.loads(data.decode())
                print(f"[DEBUG] Transcript parsed: {transcript}")
                logger.info(f"📝 Received transcript: {transcript.get('role')}: {transcript.get('content')[:50]}...")
                # Store transcript for UI or logging
                if not hasattr(streamer, 'transcript_buffer'):
                    streamer.transcript_buffer = []
                streamer.transcript_buffer.append(transcript)
                print(f"[DEBUG] Transcript stored in buffer. Total transcripts: {len(streamer.transcript_buffer)}")
            else:
                logger.info(f"Data received on topic '{topic}' from {participant.identity}")
                handle_data_channel_message(data, topic)
        except Exception as e:
            print(f"[DEBUG] ERROR in data_received: {e}")
            logger.error(f"Error in data_received handler: {e}")
            logger.error(f"Data packet: {data_packet}")
    
    # Audio processing task
    async def audio_processing_task():
        """Process incoming audio frames."""
        logger.info("Audio processing task started")
        last_delay_update = 0
        
        while streamer.running:
            try:
                audio_frame = await asyncio.wait_for(
                    streamer.audio_input_queue.get(), 
                    timeout=1.0
                )
                
                # AEC processing is already handled by parent class _input_callback
                # Do NOT apply AEC again here to avoid double processing
                
                await streamer.source.capture_frame(audio_frame)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in audio processing: {e}")
                continue
                
    # Meter display task
    async def meter_task():
        """Update the audio level meter display (adaptive mode)."""
        use_terminal = streamer.should_use_terminal_meter()
        mode = "terminal" if use_terminal else "logging"
        logger.info(f"Meter display task started ({mode} mode)")
        
        while streamer.running:
            try:
                # Use adaptive meter method that chooses based on log level
                streamer.print_audio_meter_adaptive()
                
                # Different sleep intervals based on mode
                if streamer.should_use_terminal_meter():
                    # Terminal mode: update frequently for real-time display
                    await asyncio.sleep(1.0 / stream_audio.FPS)  # ~60 FPS like original
                else:
                    # Logging mode: check frequently but only log every 2 seconds
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error updating meter: {e}")
                continue
                
    # Audio stream processing
    async def process_audio_stream(audio_stream: rtc.AudioStream, participant: rtc.RemoteParticipant):
        """Process audio stream from a remote participant."""
        logger.info(f"Starting audio processing for participant: {participant.identity}")
        async for event in audio_stream:
            if isinstance(event, rtc.AudioFrameEvent):
                # Update participant volume
                frame_data = stream_audio.np.frombuffer(event.frame.data, dtype=stream_audio.np.int16)
                rms = stream_audio.np.sqrt(stream_audio.np.mean(frame_data.astype(stream_audio.np.float32) ** 2))
                max_int16 = stream_audio.np.iinfo(stream_audio.np.int16).max
                db_level = 20.0 * stream_audio.np.log10(rms / max_int16 + 1e-6)
                
                with streamer.participants_lock:
                    if participant.sid in streamer.participants:
                        streamer.participants[participant.sid]['db_level'] = db_level
                        streamer.participants[participant.sid]['last_update'] = stream_audio.time.time()
                
                # IMPORTANT: Add received audio to output buffer for playback
                audio_data = event.frame.data.tobytes()
                with streamer.output_lock:
                    streamer.output_buffer.extend(audio_data)
    
    try:
        # Start tool server
        await tool_server.start()
        
        # Configure meters based on logging level
        use_terminal_meter = streamer.should_use_terminal_meter()
        if use_terminal_meter:
            logger.info("Using real-time terminal meters for WARNING/ERROR log level")
            # Initialize terminal UI for real-time display
            streamer.init_terminal()
        else:
            logger.info("Using logging-based meters for INFO/DEBUG log level")
        
        streamer.meter_running = True
        
        # Connect to LiveKit room
        logger.info("Connecting to LiveKit room...")
        
        # Use provided token or authenticate to get one
        if token and livekit_url:
            logger.info(f"Using provided token for participant: {participant_name}")
            room_name = None  # Will be set from room.name after connection
        else:
            # Choose authentication based on use_local flag
            if use_local:
                auth_func = authenticate_local
                logger.info("Using local authentication")
            else:
                auth_func = authenticate
                logger.info("Using remote authentication")
            
            token, room_name, livekit_url = await auth_func(participant_name, stream_audio.ROOM_NAME or "default-room")
            logger.info(f"Generated new token for participant: {participant_name}")
        
        await room.connect(livekit_url, token)
        logger.info("connected to room %s", room.name)
        
        # Register RPC method handler after connection
        room.local_participant.register_rpc_method("tool_call")(handle_tool_call)
        logger.info("RPC method 'tool_call' registered")
        
        # Publish microphone track
        logger.info("Publishing microphone track...")
        track = rtc.LocalAudioTrack.create_audio_track("mic", streamer.source)
        options = rtc.TrackPublishOptions()
        options.source = rtc.TrackSource.SOURCE_MICROPHONE
        publication = await room.local_participant.publish_track(track, options)
        logger.info("published track %s", publication.sid)
        
        # IMPORTANT: Start audio processing task BEFORE starting audio devices
        logger.info("Starting audio processing task...")
        audio_task = asyncio.create_task(audio_processing_task())
        logger.info("Audio processing task started before audio devices")
        
        # Start audio devices AFTER processing task is ready
        # This will ensure both input AND output callbacks are active for proper AEC
        logger.info("Starting audio devices...")
        streamer.start_audio_devices()
        logger.info("Audio input and output streams started - AEC callbacks active")
        
        # Start meter task with logging-compatible display
        logger.info("Starting meter task...")
        meter_display_task = asyncio.create_task(meter_task())
        
        logger.info("=== Audio streaming with tools started. Press Ctrl+C to stop. ===")
        
        # Keep running until interrupted or disconnect requested
        try:
            while streamer.running and not app_controller.disconnect_requested:
                await asyncio.sleep(1)
            
            if app_controller.disconnect_requested:
                logger.info("Stopping audio streaming due to tool request...")
            
        except KeyboardInterrupt:
            logger.info("Stopping audio streaming...")
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        # Cleanup
        logger.info("Starting cleanup...")
        streamer.running = False
        
        # Stop tool server
        await tool_server.stop()
        
        if 'audio_task' in locals():
            audio_task.cancel()
            try:
                await audio_task
            except asyncio.CancelledError:
                pass
        
        if 'meter_display_task' in locals():
            meter_display_task.cancel()
            try:
                await meter_display_task
            except asyncio.CancelledError:
                pass
        
        streamer.stop_audio_devices()
        await room.disconnect()
        await asyncio.sleep(0.5)
        
        # Clean up terminal if we were using terminal mode
        if streamer.should_use_terminal_meter():
            streamer.restore_terminal()
        
        logger.info("Cleanup complete")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LiveKit Audio Streaming with Tool Support")
    parser.add_argument(
        "--name", 
        type=str, 
        default="python-user",
        help="Participant name"
    )
    parser.add_argument(
        "--device", 
        type=int, 
        default=None,
        help="Audio device index (run list_devices.py to see available devices)"
    )
    parser.add_argument(
        "--no-aec", 
        action="store_true",
        help="Disable echo cancellation"
    )
    parser.add_argument(
        "--aec-test",
        action="store_true", 
        help="Use less aggressive AEC settings for testing"
    )
    parser.add_argument(
        "--data-channel",
        type=str,
        default="tool-calls",
        help="Name of the data channel for tool calls (default: tool-calls)"
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available tools and exit"
    )
    
    args = parser.parse_args()
    
    if args.list_tools:
        # List available tools
        from local_tool_responses import get_available_tools
        tools = get_available_tools()
        print("Available tools:")
        for name, info in tools.items():
            print(f"  - {name}: {info['description']}")
        exit(0)
    
    # Run with tools support
    aec_enabled = not args.no_aec
    if args.aec_test:
        print("Using test AEC settings with reduced aggressiveness")
    
    asyncio.run(main_with_tools(
        participant_name=args.name,
        device_index=args.device,
        enable_aec=aec_enabled,
        data_channel_name=args.data_channel
    ))