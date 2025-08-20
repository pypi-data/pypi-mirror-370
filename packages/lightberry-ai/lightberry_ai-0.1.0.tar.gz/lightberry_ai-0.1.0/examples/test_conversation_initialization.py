#!/usr/bin/env python3
"""
Test example for conversation initialization with transcript history.

This example demonstrates how to initialize a conversation with existing transcripts,
bypassing the welcome message and continuing from a specific conversation state.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the parent package to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lightberry_ai import LBBasicClient, LBToolClient

load_dotenv()

async def test_basic_client_with_history():
    """Test LBBasicClient with initial transcript history."""
    
    print("=== Testing LBBasicClient with Initial Transcripts ===")
    
    # Sample conversation history
    initial_transcripts = [
        {
            "role": "user",
            "content": "Hello, I need help with my coffee order.",
            "timestamp": 1704067200000
        },
        {
            "role": "assistant", 
            "content": "Hi! I'd be happy to help you with your coffee order. What would you like?",
            "timestamp": 1704067205000
        },
        {
            "role": "user",
            "content": "I want a large latte with oat milk.",
            "timestamp": 1704067210000
        },
        {
            "role": "assistant",
            "content": "Perfect! I'll add a large latte with oat milk to your order. Anything else?",
            "timestamp": 1704067215000
        }
    ]
    
    # Get credentials from environment
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        print("❌ Error: LIGHTBERRY_API_KEY and DEVICE_ID must be set in .env file")
        return False
    
    # Create client with initial transcripts
    client = LBBasicClient(
        api_key=api_key,
        device_id=device_id,
        initial_transcripts=initial_transcripts,
        log_level="INFO"
    )
    
    try:
        print("🔗 Connecting to Lightberry service...")
        await client.connect()
        
        print(f"✅ Connected! Room: {client.room_name}")
        print(f"📝 Client initialized with {len(initial_transcripts)} transcript messages")
        print("🎤 The conversation should continue from where we left off...")
        print("Expected: The assistant should not give a welcome greeting")
        print("Expected: The conversation should continue as if we're in the middle of ordering coffee")
        
        # Give a brief moment to see any immediate responses
        print("\n⏳ Starting audio streaming for 30 seconds to test conversation continuation...")
        
        # This will run for a short time to test the conversation flow
        audio_task = asyncio.create_task(client.enable_audio())
        
        # Wait for 30 seconds or until interrupted
        try:
            await asyncio.wait_for(audio_task, timeout=30.0)
        except asyncio.TimeoutError:
            print("⏰ Test completed (30 seconds elapsed)")
            
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await client.disconnect()
        print("🔌 Disconnected")

async def test_tool_client_with_history():
    """Test LBToolClient with initial transcript history."""
    
    print("\n=== Testing LBToolClient with Initial Transcripts ===")
    
    # Sample conversation history with tool interaction
    initial_transcripts = [
        {
            "role": "user",
            "content": "Can you help me turn on the lights?",
            "timestamp": 1704067200000
        },
        {
            "role": "assistant",
            "content": "Of course! I can help you control the lights. Which room would you like me to turn on?",
            "timestamp": 1704067205000
        },
    ]
    
    # Get credentials from environment
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        print("❌ Error: LIGHTBERRY_API_KEY and DEVICE_ID must be set in .env file")
        return False
    
    # Create tool client with initial transcripts
    client = LBToolClient(
        api_key=api_key,
        device_id=device_id,
        initial_transcripts=initial_transcripts,
        log_level="INFO"
    )
    
    try:
        print("🔗 Connecting to Lightberry service...")
        await client.connect()
        
        print(f"✅ Connected! Room: {client.room_name}")
        print(f"📝 Client initialized with {len(initial_transcripts)} transcript messages")
        print("🛠️ The conversation should continue with tool capabilities...")
        print("Expected: The assistant should not give a welcome greeting")
        print("Expected: The conversation should continue as if we're discussing smart home controls")
        
        print("\n⏳ Starting audio streaming for 30 seconds to test tool integration...")
        
        # This will run for a short time to test the conversation flow
        audio_task = asyncio.create_task(client.enable_audio())
        
        # Wait for 30 seconds or until interrupted
        try:
            await asyncio.wait_for(audio_task, timeout=30.0)
        except asyncio.TimeoutError:
            print("⏰ Test completed (30 seconds elapsed)")
            
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await client.disconnect()
        print("🔌 Disconnected")

async def test_no_transcripts():
    """Test normal behavior without initial transcripts (should give welcome message)."""
    
    print("\n=== Testing Normal Behavior (No Initial Transcripts) ===")
    
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
        # No initial_transcripts parameter - should use default welcome flow
        log_level="INFO"
    )
    
    try:
        print("🔗 Connecting to Lightberry service...")
        await client.connect()
        
        print(f"✅ Connected! Room: {client.room_name}")
        print("💬 No initial transcripts provided")
        print("Expected: The assistant should give a normal welcome greeting")
        
        print("\n⏳ Starting audio streaming for 15 seconds to verify normal welcome flow...")
        
        # This will run for a short time to test the normal flow
        audio_task = asyncio.create_task(client.enable_audio())
        
        # Wait for 15 seconds or until interrupted
        try:
            await asyncio.wait_for(audio_task, timeout=15.0)
        except asyncio.TimeoutError:
            print("⏰ Test completed (15 seconds elapsed)")
            
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await client.disconnect()
        print("🔌 Disconnected")

async def main():
    """Run all tests."""
    print("🧪 Conversation Initialization Feature Tests")
    print("=" * 50)
    
    results = []
    
    # Test 1: Basic client with history
    results.append(await test_basic_client_with_history())
    
    # Test 2: Tool client with history  
    results.append(await test_tool_client_with_history())
    
    # Test 3: Normal behavior (control test)
    results.append(await test_no_transcripts())
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    
    if all(results):
        print("🎉 All tests completed successfully!")
        print("\n📋 Manual Verification Checklist:")
        print("  □ No welcome greeting when using initial transcripts")
        print("  □ Conversation continues from provided history")
        print("  □ Real-time transcript sync via data channel")
        print("  □ Normal welcome greeting when no transcripts provided")
        print("  □ Tool functionality works with transcript history")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return all(results)

if __name__ == "__main__":
    asyncio.run(main())