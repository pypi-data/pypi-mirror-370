"""
Example: Stream with Session Instructions

This example demonstrates how to provide session-specific instructions that will be
appended to the assistant's system prompt for the duration of the session.

Session instructions allow you to customize the assistant's behavior on a per-session
basis without modifying the assistant's configuration in Airtable.

Use cases:
- Providing user-specific context or preferences
- Setting temporary behavioral modifications
- Including session-specific information like current date/time, location, etc.
- Testing different prompts without changing the assistant configuration
"""

import asyncio
import logging
import os
from datetime import datetime
from lightberry_ai import LBToolClient
from local_tool_responses import TOOL_REGISTRY, set_app_controller
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    # Get device credentials from environment
    api_key = os.environ.get("LIGHTBERRY_API_KEY")
    device_id = os.environ.get("DEVICE_ID")
    
    if not api_key or not device_id:
        print("Error: Please set LIGHTBERRY_API_KEY and DEVICE_ID environment variables")
        print("Example:")
        print("  export LIGHTBERRY_API_KEY='lb_live_...'")
        print("  export DEVICE_ID='your_device_id'")
        return
    
    # Create session-specific instructions
    # These will be appended to the assistant's system prompt for this session only
    session_instructions = f"""
For this session only, please follow these additional instructions:

1. Today's date and time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}

2. User Preferences:
   - The user prefers oat milk in their coffee
   - They like their coffee extra hot
   - They usually order a large size Iced Latte with oatmilk

3. Session Context:
   - This is a morning coffee order session
   - The user is in a hurry today
   - Please be extra concise in your responses

4. Special Instructions:
   - Always confirm the order details before sending
   - Mention any wait times if known
   - Offer to save their preferences for next time

Remember: These instructions apply only to this session.
"""
    
    print("=" * 60)
    print("Lightberry AI SDK - Session Instructions Example")
    print("=" * 60)
    print("\nSession instructions that will be added to the assistant:")
    print("-" * 40)
    print(session_instructions)
    print("-" * 40)
    print("\nConnecting to Lightberry with session-specific instructions...")
    print("The assistant will now have additional context about your preferences.")
    print("\nTry ordering a coffee to see how the session instructions affect the conversation!")
    print("\nPress Ctrl+C to exit\n")
    
    # Initialize the tool client with session instructions
    client = LBToolClient(
        api_key=api_key,
        device_id=device_id,
        enable_aec=True,
        log_level="WARNING",
        session_instructions=session_instructions  # Pass the session instructions here
    )
    
    # Set the app controller for session control
    set_app_controller(client)
    
    # Display available tools
    if TOOL_REGISTRY:
        print("\n📦 Available tools for this session:")
        for tool_name, tool_func in TOOL_REGISTRY.items():
            description = getattr(tool_func, '_tool_description', 'No description')
            print(f"  • {tool_name}: {description}")
        print()
    
    try:
        # Connect and run the client
        await client.connect()
        
        print("\n🎤 Microphone active - start speaking!")
        print("💡 The assistant now knows your coffee preferences from the session instructions")
        print("🛑 Press Ctrl+C to disconnect\n")
        
        # Start audio streaming - this blocks until interrupted
        await client.enable_audio()
            
    except KeyboardInterrupt:
        print("\n\n👋 Disconnecting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()
        print("✅ Disconnected successfully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
