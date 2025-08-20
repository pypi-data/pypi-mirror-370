# Lightberry SDK Examples

This directory contains working examples demonstrating how to use the Lightberry SDK.

## Setup

1. **Install the SDK** (see main README for installation instructions)

2. **Configure environment variables** in your project's `.env` file:
```bash
LIGHTBERRY_API_KEY=your_api_key
DEVICE_ID=your_device_id
```

3. **Copy tool definitions** to your working directory:
```bash
cp examples/local_tool_responses.py .
```

## Examples

### Basic Audio Streaming (`basic_audio_example.py`)

**Purpose**: Demonstrates audio-only streaming without tool support.

**Usage**:
```bash
python examples/basic_audio_example.py
```

**What it shows**:
- Creating and configuring a `LBBasicClient`
- Authenticating with API key and device ID
- Starting audio streaming with echo cancellation
- Handling connection lifecycle (connect → stream → disconnect)

### Tool-Enabled Streaming (`tool_client_example.py`)

**Purpose**: Demonstrates audio streaming with AI tool execution capabilities.

**Usage**:
```bash
# Ensure local_tool_responses.py is in your current directory
python examples/tool_client_example.py
```

**What it shows**:
- Creating and configuring a `LBToolClient`
- Automatic loading of tools from `local_tool_responses.py`
- Handling remote AI tool calls via data channels
- Integration between AI agent decisions and local hardware/software

### Conversation Initialization (`passing_transcript_example.py`)

**Purpose**: Demonstrates how to initialize conversations with existing transcript history, bypassing welcome messages and continuing from a specific conversation state.

**Usage**:
```bash
# Run all demos (basic client + tool client + control)
python examples/passing_transcript_example.py

# Run specific demo modes
python examples/passing_transcript_example.py --mode basic    # Basic client with transcripts
python examples/passing_transcript_example.py --mode tool     # Tool client with transcripts  
python examples/passing_transcript_example.py --mode control  # No transcripts (control)

# Use custom transcript file
python examples/passing_transcript_example.py --transcripts-file my_conversation.json
```

**What it shows**:
- Loading transcript history from JSON data, files, or environment variables
- Using `LBBasicClient` with conversation history for seamless reconnections
- Using `LBToolClient` with smart home conversation context
- Comparison between transcript-initialized and normal conversation flows
- Expected behaviors: welcome message skipping, conversation continuity

**Transcript JSON Format**:
```json
[
  {
    "role": "user",
    "content": "Hello, I need help with my order.",
    "timestamp": 1704067200000
  },
  {
    "role": "assistant", 
    "content": "Hi! I'd be happy to help with your order. What do you need?",
    "timestamp": 1704067205000
  }
]
```

**Use Cases**:
- 🔄 **Reconnection Scenarios**: Continue conversations after network disconnections
- 🧪 **Testing Specific States**: Start tests from particular conversation points
- 📱 **User Experience**: Eliminate repetitive greetings during session restoration
- 🎯 **Context Preservation**: Maintain conversation context across client restarts

## Custom Tools

**Important**: The `local_tool_responses.py` file must be in the same directory where you run your script.

To add custom tools, edit `local_tool_responses.py` in your project directory:

```python
@tool(name="my_custom_tool", description="Does something useful")
def my_function(param1: str, param2: int = 42) -> dict:
    print(f"Tool called: my_custom_tool with {param1}, {param2}")
    return {"result": "success", "processed": param1}
```

### Tool Setup
1. Copy `examples/local_tool_responses.py` to your project directory
2. Modify it to add your custom tools
3. Run your script from the same directory

### Available Example Tools
The example `local_tool_responses.py` includes:
- `template` - Demonstration tool that echoes arguments
- Coffee order tools: `add_to_order`, `get_current_order`, `amend_order`, `send_order`
- `end_session` - Gracefully disconnect from the session

Tools are automatically available to `LBToolClient` instances.

## Running the Examples

### From the SDK Directory
```bash
# Run from the lightberry_ai_sdk directory
cd lightberry_ai_sdk

# Basic audio streaming
python examples/basic_audio_example.py

# Tool-enabled streaming (requires local_tool_responses.py in current directory)
cp examples/local_tool_responses.py .
python examples/tool_client_example.py
```

### From Your Project Directory
```bash
# Copy tools file to your project
cp lightberry_ai_sdk/examples/local_tool_responses.py .

# Run examples with absolute paths
python lightberry_ai_sdk/examples/basic_audio_example.py
python lightberry_ai_sdk/examples/tool_client_example.py
```

## Key Configuration Options

Both examples support common configuration parameters:
- `device_index=None` - Audio device selection (None for system default)
- `enable_aec=True` - Acoustic echo cancellation
- `log_level="INFO"` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `assistant_name=None` - Override configured assistant (⚠️  testing only!)

### Assistant Override Example (`assistant_override_example.py`)

**Purpose**: Demonstrates how to override the configured assistant for testing.

**Usage**:
```bash
python examples/assistant_override_example.py
```

**What it shows**:
- Using the `assistant_name` parameter to specify a different assistant
- ⚠️  WARNING: This feature is for testing only and will show a warning
- Useful for testing different assistant versions without changing device config

**Important Note**: If multiple assistants with the same name exist on your account, the system will select the first one found in the lookup.