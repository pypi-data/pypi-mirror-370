# Lightberry AI SDK

A Python SDK for real-time audio streaming with AI tool execution capabilities using LiveKit infrastructure.

## Features

- **Real-time audio streaming** at 48kHz with configurable echo cancellation
- **AI tool execution** via LiveKit data channels for remote function calls
- **Two client types**: Basic audio-only streaming and tool-enabled streaming
- **Terminal audio meters** with logging-friendly alternatives
- **Standalone SDK** with no dependencies on external script files
- **Local mode support** for development and testing with self-hosted LiveKit server

## Installation

Install the SDK from the project directory:

```bash
cd lightberry_ai_sdk
pip install -e .
```

## Quick Start

### Basic Audio Streaming

```python
import asyncio
from lightberry_ai import LBBasicClient

async def main():
    client = LBBasicClient(
        api_key="your_api_key",
        device_id="your_device_id",
        enable_aec=True
    )
    
    await client.connect()
    await client.enable_audio()

asyncio.run(main())
```

### Tool-Enabled Streaming

```python
import asyncio
from lightberry_ai import LBToolClient

async def main():
    client = LBToolClient(
        api_key="your_api_key", 
        device_id="your_device_id"
    )
    
    await client.connect()
    await client.enable_audio()  # Tools automatically available

asyncio.run(main())
```

## Configuration

### Environment Variables

Create a `.env` file in your project:

```bash
LIGHTBERRY_API_KEY=your_api_key
DEVICE_ID=your_device_id
```

### Client Parameters

Both client classes support these parameters:

- `api_key` (str, optional): Lightberry API key for authentication (required for remote mode)
- `device_id` (str, optional): Device identifier for multi-device management (required for remote mode)
- `use_local` (bool): Use local LiveKit server instead of cloud (default: False)
- `device_index` (int, optional): Audio device index (None for default)
- `enable_aec` (bool): Enable acoustic echo cancellation (default: True)
- `log_level` (str): Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)
- `assistant_name` (str, optional): Override configured assistant (⚠️  testing only!) - If multiple assistants with the same name exist, the first one found will be used
- `initial_transcripts` (list, optional): Initialize conversation with transcript history (see Conversation Initialization)
- `session_instructions` (str, optional): Custom instructions appended to system prompt for this session only (see Session Instructions)

## Local Mode (Coming Soon)

Local mode for development and testing without cloud resources is coming soon. This will allow you to:

- Test your applications without API keys
- Run everything locally on your machine  
- Use an echo bot for audio testing
- Debug with full access to server logs

For early access and documentation, see the [local mode setup guide](../local-livekit/LOCAL_MODE_README.md).

**Note:** Local mode support is currently in development and will be fully supported in an upcoming release.

## Conversation Initialization

Initialize conversations with existing transcript history to bypass welcome messages and continue from a specific conversation state.

### Basic Usage

```python
import asyncio
from lightberry_ai import LBBasicClient

# Define conversation history
conversation_history = [
    {
        "role": "user",
        "content": "Hello, I need help with my order status.",
        "timestamp": 1704067200000  # Optional timestamp
    },
    {
        "role": "assistant", 
        "content": "Hi! I'd be happy to help you check your order status. What's your order number?",
        "timestamp": 1704067205000
    },
    {
        "role": "user",
        "content": "My order number is #12345.",
        "timestamp": 1704067210000
    }
]

async def main():
    client = LBBasicClient(
        api_key="your_api_key",
        device_id="your_device_id",
        initial_transcripts=conversation_history  # Initialize with history
    )
    
    await client.connect()
    await client.enable_audio()  # Conversation continues from transcript history

asyncio.run(main())
```

### Tool Client with Transcripts

```python
from lightberry_ai import LBToolClient

# Smart home conversation history
smart_home_history = [
    {
        "role": "user",
        "content": "Can you help me control the lights in my living room?"
    },
    {
        "role": "assistant",
        "content": "Of course! I can help you control the smart lights. Which lights would you like me to adjust?"
    },
    {
        "role": "user",
        "content": "Turn on the main ceiling light and set it to 75% brightness."
    }
]

async def main():
    client = LBToolClient(
        api_key="your_api_key",
        device_id="your_device_id",
        initial_transcripts=smart_home_history  # Tools + conversation history
    )
    
    await client.connect()
    await client.enable_audio()  # Tools available + conversation context

asyncio.run(main())
```

### Loading from JSON File

```python
import json

def load_conversation_from_file(file_path: str) -> list:
    """Load conversation history from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

# conversation_history.json format:
# [
#   {"role": "user", "content": "Hello", "timestamp": 1704067200000},
#   {"role": "assistant", "content": "Hi there!", "timestamp": 1704067205000}
# ]

conversation = load_conversation_from_file("conversation_history.json")
client = LBBasicClient(..., initial_transcripts=conversation)
```

### Environment Variable Loading

```python
import os
import json

# Load from INITIAL_TRANSCRIPTS environment variable
transcripts_json = os.getenv("INITIAL_TRANSCRIPTS")
if transcripts_json:
    transcripts = json.loads(transcripts_json)
    client = LBBasicClient(..., initial_transcripts=transcripts)
```

### Expected Behavior

**With Initial Transcripts:**
- ✅ Welcome message is skipped
- ✅ Conversation continues from provided history
- ✅ AI agent has full context of previous exchanges
- ✅ Real-time transcript sync via data channels

**Without Initial Transcripts:**
- ✅ Normal welcome greeting occurs
- ✅ Conversation starts fresh

### Transcript Format

Each transcript entry supports:

```python
{
    "role": "user" | "assistant",     # Required: Speaker role
    "content": "Message content",     # Required: Transcript text
    "timestamp": 1704067200000        # Optional: Unix timestamp in milliseconds
}
```

## Assistant Override (Testing)

Override the configured assistant with a different one for testing purposes. This allows testing different assistant personalities and configurations without changing your device settings.

### ⚠️ Important Notes

- **Testing Only**: Assistant override should only be used for testing and development
- **Warning Messages**: The SDK will display warnings when using assistant override
- **Name Lookup**: If multiple assistants have the same name, the first one found will be used
- **Temporary Override**: This only affects the current session, not your device configuration

### Basic Usage

```python
import asyncio
from lightberry_ai import LBBasicClient

async def main():
    # Override the configured assistant with a specific one
    client = LBBasicClient(
        api_key="your_api_key",
        device_id="your_device_id",
        assistant_name="Test Assistant"  # Override with different assistant
    )
    
    await client.connect()  # Will show warning about override
    await client.enable_audio()

asyncio.run(main())
```

### Tool Client Override

```python
import asyncio
from lightberry_ai import LBToolClient

async def main():
    # Test tools with a different assistant
    client = LBToolClient(
        api_key="your_api_key",
        device_id="your_device_id", 
        assistant_name="Smart Home Assistant"  # Override for specific use case
    )
    
    await client.connect()
    await client.enable_audio()  # Tools + different assistant personality

asyncio.run(main())
```

### Testing Multiple Assistants

```python
async def test_different_assistants():
    """Test the same functionality with different assistants"""
    
    assistants_to_test = [
        "Customer Service Bot",
        "Technical Support Agent", 
        "Friendly Companion"
    ]
    
    for assistant_name in assistants_to_test:
        print(f"\\n🧪 Testing with: {assistant_name}")
        
        client = LBBasicClient(
            api_key="your_api_key",
            device_id="your_device_id",
            assistant_name=assistant_name
        )
        
        await client.connect()
        print(f"✅ Connected with {assistant_name}")
        
        # Quick interaction test
        # await client.enable_audio()  # Uncomment for full test
        
        await client.disconnect()
        print(f"🔌 Disconnected from {assistant_name}")

asyncio.run(test_different_assistants())
```

### Expected Behavior

**When using assistant override:**
- ⚠️  **Warning message displayed**: `WARNING: Manually overwriting the assistant`
- ✅ **Authentication includes override**: API call includes the override assistant name
- ✅ **Server loads specified assistant**: The requested assistant is loaded instead of default
- ✅ **All functionality works**: Audio streaming, tools, and features work normally

**Console Output Example:**
```
WARNING:lightberry_ai.auth.authenticator:⚠️  WARNING: Manually overwriting the assistant to a different one than is configured. Use this only for testing.
INFO:lightberry_ai.auth.authenticator:Attempting to fetch credentials for assistant: Test Assistant
INFO:lightberry_ai.core.basic_client:Successfully authenticated - Room: lightberry
```

### Use Cases

1. **A/B Testing**: Compare different assistant personalities for the same task
2. **Feature Testing**: Test specific assistant configurations with new features
3. **Development**: Develop with a test assistant instead of production assistant
4. **Quality Assurance**: Validate functionality across multiple assistant types

## Session Instructions

Provide session-specific instructions that temporarily modify the assistant's behavior without changing its core configuration. These instructions are appended to the system prompt for the duration of the session only.

### Basic Usage

```python
import asyncio
from datetime import datetime
from lightberry_ai import LBBasicClient

async def main():
    # Create custom instructions for this session
    session_instructions = f"""
    For this session only:
    - Current date and time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}
    - The user prefers brief, concise responses
    - Focus on technical details when explaining concepts
    """
    
    client = LBBasicClient(
        api_key="your_api_key",
        device_id="your_device_id",
        session_instructions=session_instructions  # Apply session-specific behavior
    )
    
    await client.connect()
    await client.enable_audio()

asyncio.run(main())
```

### Example: Continuing a Lesson

Resume a programming lesson from where the student left off:

```python
import asyncio
import json
from lightberry_ai import LBBasicClient

# Load student's progress from storage
def load_student_progress(student_id: str) -> dict:
    with open(f"progress/{student_id}.json", "r") as f:
        return json.load(f)

async def main():
    student_id = "student_123"
    progress = load_student_progress(student_id)
    
    # Create session instructions based on student progress
    session_instructions = f"""
    STUDENT PROGRESS CONTEXT:
    
    Student: {progress['name']}
    Current Course: {progress['course']}
    Last Lesson: {progress['last_lesson']}
    Topics Completed: {', '.join(progress['completed_topics'])}
    Current Topic: {progress['current_topic']}
    Struggles With: {', '.join(progress['difficulty_areas'])}
    
    INSTRUCTIONS FOR THIS SESSION:
    1. We are continuing from lesson {progress['last_lesson']} on {progress['current_topic']}
    2. The student has already covered: {', '.join(progress['completed_topics'])}
    3. No need to review completed topics unless the student asks
    4. Pay special attention to: {', '.join(progress['difficulty_areas'])}
    5. Use examples related to: {progress['preferred_examples']}
    6. Teaching style preference: {progress['learning_style']}
    
    Start by briefly confirming we're continuing from {progress['current_topic']} 
    and ask if they're ready to proceed.
    """
    
    client = LBBasicClient(
        api_key="your_api_key",
        device_id="your_device_id",
        session_instructions=session_instructions
    )
    
    await client.connect()
    print(f"📚 Resuming lesson for {progress['name']} - {progress['current_topic']}")
    await client.enable_audio()

asyncio.run(main())
```

### Example: Recognizing a Customer

Personalize interactions based on customer history and preferences:

```python
import asyncio
from datetime import datetime
from lightberry_ai import LBToolClient

# Fetch customer data from your CRM/database
def get_customer_profile(customer_id: str) -> dict:
    # In production, this would query your database
    return {
        "name": "Sarah Johnson",
        "customer_since": "2021",
        "vip_status": True,
        "preferred_coffee": "Oat Milk Cappuccino",
        "usual_size": "Large",
        "allergies": ["nuts", "soy"],
        "last_orders": [
            "Large Oat Milk Cappuccino with extra shot",
            "Medium Almond Croissant (cancelled - allergy)",
            "Large Oat Milk Latte"
        ],
        "preferences": {
            "temperature": "extra hot",
            "sweetness": "no sugar",
            "loyalty_points": 2847
        }
    }

async def main():
    customer_id = "cust_98765"
    customer = get_customer_profile(customer_id)
    
    # Build personalized session instructions
    session_instructions = f"""
    RECOGNIZED CUSTOMER - VIP PROFILE:
    
    Customer: {customer['name']}
    Status: {'VIP ⭐' if customer['vip_status'] else 'Regular'} customer since {customer['customer_since']}
    Loyalty Points: {customer['preferences']['loyalty_points']} points
    
    PREFERENCES:
    - Usual Order: {customer['preferred_coffee']} ({customer['usual_size']})
    - Temperature: {customer['preferences']['temperature']}
    - Sweetness: {customer['preferences']['sweetness']}
    
    IMPORTANT ALLERGIES: {', '.join(customer['allergies'])}
    - Never recommend items containing these ingredients
    - Double-check any food orders for allergens
    
    RECENT ORDER HISTORY:
    {chr(10).join(f"  - {order}" for order in customer['last_orders'])}
    
    INTERACTION GUIDELINES:
    1. Greet by name: "Welcome back, {customer['name'].split()[0]}!"
    2. You may suggest their usual order: "{customer['usual_size']} {customer['preferred_coffee']}"
    3. Remember their preferences without them having to repeat
    4. If they order food, proactively check for {', '.join(customer['allergies'])}
    5. Mention loyalty points if relevant to their order
    6. Provide personalized recommendations based on their history
    
    Today's date: {datetime.now().strftime('%A, %B %d, %Y')}
    Special: Buy 2 get 3rd free on all pastries (except items with nuts)
    """
    
    client = LBToolClient(
        api_key="your_api_key",
        device_id="your_device_id",
        session_instructions=session_instructions
    )
    
    await client.connect()
    print(f"👤 Customer recognized: {customer['name']} (VIP: {customer['vip_status']})")
    await client.enable_audio()

asyncio.run(main())
```

### Use Cases for Session Instructions

1. **Educational Continuity**: Resume lessons with full context of student progress
2. **Customer Recognition**: Provide personalized service based on customer history
3. **Temporal Context**: Include current date, time, location, or events
4. **User Preferences**: Apply user-specific interaction styles or preferences
5. **Business Context**: Include inventory status, daily specials, or operational updates
6. **Accessibility Needs**: Adjust communication style for specific user requirements
7. **Session Goals**: Define specific objectives or constraints for the interaction

### Session Instructions vs Initial Transcripts

| Feature | Session Instructions | Initial Transcripts |
|---------|---------------------|-------------------|
| **Purpose** | Modify assistant behavior | Continue conversation history |
| **Affects** | System prompt (how AI behaves) | Conversation context (what was said) |
| **Use When** | You need different behavior | You need conversation continuity |
| **Example** | "Be more concise", "User is VIP" | Previous chat messages |
| **Persistence** | Session only | Session only |

### Best Practices

1. **Keep Instructions Focused**: Include only relevant context for the current session
2. **Use Structured Format**: Organize instructions with clear sections and bullet points
3. **Include Temporal Context**: Add current date/time when relevant
4. **Security**: Never include sensitive data like passwords or payment information
5. **Update Dynamically**: Generate instructions based on real-time data from your systems
6. **Test Thoroughly**: Verify the assistant behaves as expected with your instructions

## Custom Tools

### Tool Architecture

Tools in Lightberry AI follow a two-part architecture:

1. **Server-side Definition**: Tools are defined and configured on the **Lightberry Dashboard** where you specify:
   - Tool names and descriptions
   - Parameter schemas and types
   - When the AI agent should call each tool
   
2. **Client-side Implementation**: The `local_tool_responses.py` file defines **how** each tool executes on your device:

```python
from local_tool_responses import tool

@tool(name="move_robot_arm", description="Moves robot arm to position")
def handle_arm_movement(x: float, y: float, z: float) -> dict:
    # Your implementation here - integrate with existing robot control
    robot_controller.move_arm_to(x, y, z)
    return {"result": "success", "position": [x, y, z]}

@tool(name="add_to_order", description="Add item to coffee order")
def add_coffee_item(coffee_type: str, milk_type: str, size: str = "medium") -> dict:
    # Integration with coffee machine API
    coffee_machine.add_order_item(coffee_type, milk_type, size)
    print(f"☕ Added {size} {coffee_type} with {milk_type} milk to order")
    return {"result": "success", "item_added": True}
```

### Workflow

1. **Configure on Dashboard**: Define tools, parameters, and AI behavior on the Lightberry Dashboard
2. **Implement Locally**: Create `local_tool_responses.py` with functions that handle the actual execution
3. **Tool Matching**: When the AI calls a tool, it's routed to your local implementation by name

This separation allows you to:
- Configure AI behavior centrally via the dashboard
- Implement tool execution using your existing codebase and hardware integrations
- Update tool logic locally without changing server configuration

### Current Limitations

**⚠️ Tool Response Feedback**: The AI agent currently does not receive feedback from locally executed tool calls. While your tools execute successfully and can return data, this information is not sent back to the AI agent for follow-up conversations.

**🚀 Coming Soon**: Tool response feedback functionality is in development and will allow the AI agent to:
- Receive and process tool execution results
- Make follow-up decisions based on tool outcomes
- Provide more contextual responses about completed actions

**Important**: The `local_tool_responses.py` file must be in the same directory where you run your script.

## Examples

Complete working examples are available in the [`examples/`](examples/) directory:

- **[`basic_audio_example.py`](examples/basic_audio_example.py)** - Audio-only streaming
- **[`tool_client_example.py`](examples/tool_client_example.py)** - Tool-enabled streaming
- **[`local_mode_example.py`](examples/local_mode_example.py)** - Local LiveKit server connection for development
- **[`passing_transcript_example.py`](examples/passing_transcript_example.py)** - Conversation initialization with transcript history
- **[`assistant_override_example.py`](examples/assistant_override_example.py)** - Assistant override for testing (⚠️ testing only)
- **[`stream_session_instructions.py`](examples/stream_session_instructions.py)** - Session-specific instructions for personalization
- **[`local_tool_responses.py`](examples/local_tool_responses.py)** - Example tool definitions

### Running Examples

```bash
# Copy the tool definitions to your working directory
cp examples/local_tool_responses.py .

# Run basic audio streaming
python examples/basic_audio_example.py

# Run tool-enabled streaming  
python examples/tool_client_example.py

# Run local mode examples (requires local LiveKit server)
python examples/local_mode_example.py

# Run transcript initialization demo (shows both basic and tool clients)
python examples/passing_transcript_example.py

# Run specific transcript demo modes
python examples/passing_transcript_example.py --mode basic    # Basic client only
python examples/passing_transcript_example.py --mode tool     # Tool client only
python examples/passing_transcript_example.py --mode control  # No transcripts (control)

# Run assistant override examples (⚠️ testing only)
python examples/assistant_override_example.py                 # Simple assistant override demo

# Run session instructions example
python examples/stream_session_instructions.py                # Personalized session with custom instructions
```

See the [examples README](examples/README.md) for detailed usage instructions.

## API Reference

### LightberryBasicClient

Audio-only streaming client.

**Methods:**
- `await connect()` - Authenticate and connect to LiveKit room
- `await enable_audio()` - Enable bidirectional audio streaming (blocks until stopped)
- `await disconnect()` - Disconnect and cleanup

**Properties:**
- `is_connected` - Connection status
- `participant_name` - Assigned participant name
- `room_name` - Assigned room name

### LightberryToolClient

Audio streaming with tool execution support. Inherits all `LightberryBasicClient` functionality.

**Additional Properties:**
- `data_channel_name` - Data channel used for tool communication

**Tool System:**
- Automatically loads tools from `local_tool_responses.py`
- Supports both sync and async tool functions
- Tools receive JSON parameters as keyword arguments
- Tools can control application lifecycle (e.g., `end_session`)

## Audio Configuration

- **Sample Rate**: 48kHz
- **Channels**: Mono
- **Frame Size**: 10ms (480 samples)
- **Echo Cancellation**: Configurable AEC with AudioProcessingModule
- **Audio Meters**: Adaptive display (terminal or logging-based)

## Requirements

- Python 3.10+
- LiveKit Python SDK
- SoundDevice for audio I/O
- NumPy for audio processing
- aiohttp for API communication
- python-dotenv for environment variables

## Troubleshooting

### Tool Import Issues
```
WARNING: local_tool_responses.py not found - no tools will be available
```
**Solution**: Copy `examples/local_tool_responses.py` to your project directory.

### Audio Device Issues
Use `list_devices.py` from the original project to find the correct `device_index`.

### Connection Issues
Verify your `.env` file contains valid `LIGHTBERRY_API_KEY` and `DEVICE_ID`.

### Assistant Override Issues
```
Assistant 'AssistantName' not found
```
**Solution**: Check that the assistant name exists in your Airtable configuration and is spelled correctly.

```
WARNING: Manually overwriting the assistant...
```
**Expected**: This warning appears when using `assistant_name` parameter - this is normal for testing.

## License

See [LICENSE](LICENSE) file for details.