#!/usr/bin/env python3
"""
Transcript Passing Example

This example demonstrates how to use both LBBasicClient and LBToolClient with 
initial transcript history to initialize conversations from a specific point.

Features demonstrated:
- Loading initial transcripts from JSON file or environment variable
- Using LBBasicClient with conversation history
- Using LBToolClient with conversation history  
- Bypassing welcome messages with transcript initialization
- Handling both basic and tool-enabled conversation flows
"""

import asyncio
import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from lightberry_ai import LBBasicClient, LBToolClient

# Sample transcript data for demonstrations
SAMPLE_BASIC_CONVERSATION = [
    {
        "role": "user",
        "content": "Hello, I need help with my order status.",
        "timestamp": 1704067200000
    },
    {
        "role": "assistant", 
        "content": "Hi! I'd be happy to help you check your order status. What's your order number?",
        "timestamp": 1704067205000
    },
    {
        "role": "user",
        "content": "My order number is #12345. I placed it yesterday.",
        "timestamp": 1704067210000
    }
]

SAMPLE_TOOL_CONVERSATION = [
    {
        "role": "user",
        "content": "Can you help me control the smart lights in my living room?",
        "timestamp": 1704067200000
    },
    {
        "role": "assistant",
        "content": "Of course! I can help you control the smart lights. Which lights would you like me to adjust?",
        "timestamp": 1704067205000
    },
    {
        "role": "user",
        "content": "Turn on the main ceiling light and set it to 75% brightness please.",
        "timestamp": 1704067210000
    }
]

def load_transcripts_from_file(file_path: str) -> list:
    """Load transcripts from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            transcripts = json.load(f)
        print(f"📝 Loaded {len(transcripts)} transcripts from {file_path}")
        return transcripts
    except FileNotFoundError:
        print(f"❌ Transcript file {file_path} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing transcript file: {e}")
        return None

def load_transcripts_from_env() -> list:
    """Load transcripts from environment variable"""
    transcripts_json = os.getenv("INITIAL_TRANSCRIPTS")
    if transcripts_json:
        try:
            transcripts = json.loads(transcripts_json)
            print(f"📝 Loaded {len(transcripts)} transcripts from environment")
            return transcripts
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing INITIAL_TRANSCRIPTS environment variable: {e}")
            return None
    return None

async def demo_basic_client_with_transcripts():
    """Demonstrate LBBasicClient with initial transcript history"""
    print("\n" + "="*60)
    print("🎤 LBBasicClient with Initial Transcript History")
    print("="*60)
    
    # Get credentials from environment
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        print("❌ Error: LIGHTBERRY_API_KEY and DEVICE_ID must be set in .env file")
        return False
    
    print(f"Device ID: {device_id}")
    print(f"API Key: {api_key[:8]}..." if api_key else "Not set")
    
    # Create client with conversation history
    client = LBBasicClient(
        api_key=api_key,
        device_id=device_id,
        device_index=None,        # Use default audio device
        enable_aec=True,          # Enable echo cancellation
        log_level="INFO",         # More verbose for demo
        initial_transcripts=SAMPLE_BASIC_CONVERSATION
    )
    
    try:
        print(f"\n📝 Initializing with {len(SAMPLE_BASIC_CONVERSATION)} transcript messages:")
        for i, msg in enumerate(SAMPLE_BASIC_CONVERSATION, 1):
            print(f"  {i}. {msg['role']}: {msg['content']}")
        
        # Connect to Lightberry service
        print("\n🔗 Connecting to Lightberry service...")
        await client.connect()
        
        print(f"✅ Connected! Room: {client.room_name}, Participant: {client.participant_name}")
        print("💬 Expected: The assistant should NOT give a welcome greeting")
        print("💬 Expected: The conversation should continue from the order status context")
        
        # Start audio streaming
        print("\n🎤 Starting audio streaming for 20 seconds...")
        print("You can speak now - the conversation continues from the transcript history!")
        
        # Run for a limited time for demo purposes
        audio_task = asyncio.create_task(client.enable_audio())
        
        try:
            await asyncio.wait_for(audio_task, timeout=20.0)
        except asyncio.TimeoutError:
            print("⏰ Demo completed (20 seconds elapsed)")
            
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False
    finally:
        await client.disconnect()
        print("🔌 Disconnected from basic client demo")

async def demo_tool_client_with_transcripts():
    """Demonstrate LBToolClient with initial transcript history"""
    print("\n" + "="*60)
    print("🛠️  LBToolClient with Initial Transcript History")
    print("="*60)
    
    # Get credentials from environment
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        print("❌ Error: LIGHTBERRY_API_KEY and DEVICE_ID must be set in .env file")
        return False
    
    print(f"Device ID: {device_id}")
    print(f"API Key: {api_key[:8]}..." if api_key else "Not set")
    
    # Create tool client with smart home conversation history
    client = LBToolClient(
        api_key=api_key,
        device_id=device_id,
        log_level="INFO",         # More verbose for demo
        initial_transcripts=SAMPLE_TOOL_CONVERSATION
    )
    
    try:
        print(f"\n📝 Initializing with {len(SAMPLE_TOOL_CONVERSATION)} smart home transcript messages:")
        for i, msg in enumerate(SAMPLE_TOOL_CONVERSATION, 1):
            print(f"  {i}. {msg['role']}: {msg['content']}")
        
        # Connect to Lightberry service
        print("\n🔗 Connecting to Lightberry service...")
        await client.connect()
        
        print(f"✅ Connected! Room: {client.room_name}, Participant: {client.participant_name}")
        print("💬 Expected: The assistant should NOT give a welcome greeting")
        print("💬 Expected: The conversation should continue from the smart home lighting context")
        print("🛠️  Expected: Tool functionality should be available for light control")
        
        # Start audio streaming
        print("\n🎤 Starting audio streaming for 25 seconds...")
        print("You can speak now - ask about lights or other smart home controls!")
        
        # Run for a limited time for demo purposes
        audio_task = asyncio.create_task(client.enable_audio())
        
        try:
            await asyncio.wait_for(audio_task, timeout=25.0)
        except asyncio.TimeoutError:
            print("⏰ Demo completed (25 seconds elapsed)")
            
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False
    finally:
        await client.disconnect()
        print("🔌 Disconnected from tool client demo")

async def demo_no_transcripts():
    """Demonstrate normal behavior without transcripts (control demo)"""
    print("\n" + "="*60)
    print("🎤 Normal Behavior Demo (No Initial Transcripts)")
    print("="*60)
    
    # Get credentials from environment
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        print("❌ Error: LIGHTBERRY_API_KEY and DEVICE_ID must be set in .env file")
        return False
    
    # Create client WITHOUT initial transcripts
    client = LBBasicClient(
        api_key=api_key,
        device_id=device_id,
        log_level="INFO"
        # No initial_transcripts parameter - should use default welcome flow
    )
    
    try:
        print("💬 No initial transcripts provided")
        print("💬 Expected: The assistant should give a normal welcome greeting")
        
        # Connect to Lightberry service
        print("\n🔗 Connecting to Lightberry service...")
        await client.connect()
        
        print(f"✅ Connected! Room: {client.room_name}")
        
        # Start audio streaming
        print("\n🎤 Starting audio streaming for 15 seconds...")
        print("Listen for the welcome greeting...")
        
        audio_task = asyncio.create_task(client.enable_audio())
        
        try:
            await asyncio.wait_for(audio_task, timeout=15.0)
        except asyncio.TimeoutError:
            print("⏰ Control demo completed (15 seconds elapsed)")
            
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False
    finally:
        await client.disconnect()
        print("🔌 Disconnected from control demo")

async def main():
    """Main demo function"""
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Lightberry Transcript Passing Demo")
    parser.add_argument(
        "--mode", 
        choices=["basic", "tool", "control", "all"], 
        default="all",
        help="Which demo to run (default: all)"
    )
    parser.add_argument(
        "--transcripts-file",
        type=str,
        help="Load transcripts from JSON file instead of using samples"
    )
    
    args = parser.parse_args()
    
    print("🧪 Lightberry Transcript Passing Feature Demo")
    print("=" * 60)
    print("This demo shows how to initialize conversations with transcript history.")
    print("The conversation will continue from where the transcripts left off.")
    
    # Load transcripts from file or environment if specified
    custom_transcripts = None
    if args.transcripts_file:
        custom_transcripts = load_transcripts_from_file(args.transcripts_file)
    else:
        custom_transcripts = load_transcripts_from_env()
    
    # Use custom transcripts if loaded
    if custom_transcripts:
        global SAMPLE_BASIC_CONVERSATION, SAMPLE_TOOL_CONVERSATION
        SAMPLE_BASIC_CONVERSATION = custom_transcripts
        SAMPLE_TOOL_CONVERSATION = custom_transcripts
        print(f"🔄 Using custom transcripts with {len(custom_transcripts)} messages")
    
    results = []
    
    if args.mode in ["basic", "all"]:
        print("\n⏳ Starting Basic Client Demo...")
        results.append(await demo_basic_client_with_transcripts())
        
        if args.mode == "all":
            print("\n⏸️  Waiting 3 seconds between demos...")
            await asyncio.sleep(3)
    
    if args.mode in ["tool", "all"]:
        print("\n⏳ Starting Tool Client Demo...")
        results.append(await demo_tool_client_with_transcripts())
        
        if args.mode == "all":
            print("\n⏸️  Waiting 3 seconds between demos...")
            await asyncio.sleep(3)
    
    if args.mode in ["control", "all"]:
        print("\n⏳ Starting Control Demo...")
        results.append(await demo_no_transcripts())
    
    # Summary
    print("\n" + "="*60)
    print("🏁 Demo Summary")
    print("="*60)
    print(f"✅ Completed demos: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All demos completed successfully!")
        print("\n📋 Manual Verification Checklist:")
        print("  □ No welcome greeting when using initial transcripts")
        print("  □ Conversation continues from provided history")
        print("  □ Real-time transcript sync via data channel")
        print("  □ Normal welcome greeting when no transcripts provided")
        print("  □ Tool functionality works with transcript history")
    else:
        print("❌ Some demos failed. Check the output above for details.")
    
    return all(results)

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user. Goodbye!")
        exit(0)