"""
Local Tool Responses Module

This module allows users to define custom tool functions that can be executed
when tool calls are received via the LiveKit data channel.

To create a new tool:
1. Define a function with any name
2. Decorate it with @tool(name="tool_name")
3. The function will receive arguments from the JSON tool call

Example:
    @tool(name="get_weather")
    def fetch_weather(location: str, unit: str = "celsius") -> dict:
        # Your implementation here
        return {"temperature": 22, "unit": unit, "location": location}
"""

from typing import Any, Callable, Dict, Optional
import functools
import logging
import asyncio
from time import sleep

logger = logging.getLogger(__name__)

# Registry to store all available tools
TOOL_REGISTRY: Dict[str, Callable] = {}

# Global reference to allow tools to control the application
_app_controller = None

def set_app_controller(controller):
    """Set the app controller reference for tools that need to control the application."""
    global _app_controller
    _app_controller = controller


def tool(name: str, description: Optional[str] = None):
    """
    Decorator to register a function as a tool that can be called remotely.
    
    Args:
        name: The name that will be used to invoke this tool
        description: Optional description of what the tool does
        
    Example:
        @tool(name="calculator", description="Performs basic calculations")
        def calculate(operation: str, a: float, b: float) -> float:
            ...
    """
    def decorator(func: Callable) -> Callable:
        # Store metadata with the function
        func._tool_name = name
        func._tool_description = description or func.__doc__ or "No description available"
        
        # Register the function
        TOOL_REGISTRY[name] = func
        logger.info(f"Registered tool '{name}': {func._tool_description}")
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"Executing tool '{name}' with args={args}, kwargs={kwargs}")
                result = func(*args, **kwargs)
                logger.debug(f"Tool '{name}' completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error executing tool '{name}': {e}")
                raise
                
        return wrapper
    return decorator


def get_available_tools() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all registered tools.
    
    Returns:
        Dictionary mapping tool names to their metadata
    """
    tools = {}
    for name, func in TOOL_REGISTRY.items():
        tools[name] = {
            "name": name,
            "description": getattr(func, '_tool_description', 'No description'),
            "function": func.__name__,
            "module": func.__module__
        }
    return tools


# ============== User Tool Definitions ==============
# Users can add their own tools below this line

# Template function as requested
@tool(name="template", description="Template tool function for demonstration")
def template_function(**kwargs) -> Dict[str, Any]:
    """
    Template function that accepts any keyword arguments.
    This demonstrates how to create a flexible tool that can handle various inputs.
    
    All arguments passed in the JSON tool call will be available as kwargs.
    """
    # Print the tool name and arguments as requested
    print(f"Tool called: template")
    print(f"Arguments: {kwargs}")
    
    return {
        "tool": "template",
        "received_arguments": kwargs,
        "argument_count": len(kwargs),
        "message": "This is a template function. Replace with your own implementation."
    }


# ============== Coffee Order Tools ==============

@tool(name="add_to_order", description="Add an item to the coffee order")
def add_to_order(
    coffee_type: str,
    milk_type: str,
    size: str = "medium",
    quantity: int = 1,
    special_instructions: str = ""
) -> Dict[str, Any]:
    """Add an item to the coffee order."""
    
    # Print the order details
    special_text = f" with {special_instructions}" if special_instructions else ""
    print(f"☕ Adding to order: {quantity}x {size} {coffee_type} with {milk_type} milk{special_text}")
    
    return {
        "tool": "add_to_order",
        "success": True,
        "item": {
            "coffee_type": coffee_type,
            "milk_type": milk_type,
            "size": size,
            "quantity": quantity,
            "special_instructions": special_instructions
        },
        "message": f"Added {quantity}x {size} {coffee_type} with {milk_type} milk to order"
    }


@tool(name="get_current_order", description="Get the current coffee order")
def get_current_order() -> Dict[str, Any]:
    """Get the current coffee order."""
    
    print("📋 Getting current coffee order")
    
    return {
        "tool": "get_current_order",
        "success": True,
        "order": [],  # In a real implementation, this would contain the actual order items
        "message": "Current order retrieved (mock implementation - order is empty)"
    }


@tool(name="amend_order", description="Modify or remove an item from the current order")
def amend_order(
    item_id: str = "",
    coffee_type: str = "",
    milk_type: str = "",
    size: str = "",
    quantity: int = 0,
    special_instructions: str = "",
    action: str = "update"
) -> Dict[str, Any]:
    """Modify or remove an item from the current order."""
    
    if action == "remove":
        print(f"🗑️ Removing item {item_id} from order")
    else:
        changes = []
        if coffee_type:
            changes.append(f"coffee type: {coffee_type}")
        if milk_type:
            changes.append(f"milk type: {milk_type}")
        if size:
            changes.append(f"size: {size}")
        if quantity > 0:
            changes.append(f"quantity: {quantity}")
        if special_instructions:
            changes.append(f"special instructions: {special_instructions}")
        
        changes_text = ", ".join(changes) if changes else "no changes"
        print(f"✏️ Amending order item {item_id}: {changes_text}")
    
    return {
        "tool": "amend_order",
        "success": True,
        "item_id": item_id,
        "action": action,
        "message": f"Order item {action}d successfully"
    }


@tool(name="send_order", description="Send the current order to the coffee robot")
def send_order(customer_name: str = "", special_notes: str = "") -> Dict[str, Any]:
    """Send the current order to the coffee robot."""
    
    customer_text = f" for {customer_name}" if customer_name else ""
    notes_text = f" (Notes: {special_notes})" if special_notes else ""
    print(f"🚀 Sending coffee order to robot{customer_text}{notes_text}")
    
    return {
        "tool": "send_order",
        "success": True,
        "customer_name": customer_name,
        "special_notes": special_notes,
        "message": f"Order sent to coffee robot{customer_text}"
    }


# ============== Robot Control Tools ==============

# Add tracking dictionary at module level for duplicate prevention
_tool_call_tracker = {}

@tool(name="dance_tool", description="Trigger dance motion on robot by simulating joystick button press")
async def dance_tool(**kwargs) -> Dict[str, Any]:
    """
    Async version that triggers dance motion without blocking the event loop.
    Uses subprocess for non-blocking rostopic calls.
    """
    import subprocess
    import json
    import asyncio
    import time
    
    # Prevent duplicate calls within 1 second
    current_time = time.time()
    if 'dance_tool' in _tool_call_tracker:
        if current_time - _tool_call_tracker['dance_tool'] < 1.0:
            print("⚠️ Duplicate dance_tool call ignored (within 1 second)")
            return {
                "tool": "dance_tool",
                "success": True,
                "message": "Duplicate call ignored",
                "duplicate": True
            }
    
    _tool_call_tracker['dance_tool'] = current_time
    
    # Log any extra arguments from the AI
    if kwargs:
        print(f"🕺 Dance requested with params: {kwargs}")
    
    try:
        # Create the Joy message for button press
        joy_message_press = {
            "header": {
                "seq": 0,
                "stamp": {"secs": 0, "nsecs": 0},
                "frame_id": "/dev/input/js0"
            },
            "axes": [0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0],
            "buttons": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        
        # Publish button press using subprocess (non-blocking)
        print("🕺 Triggering dance motion - button press")
        cmd_press = [
            "rostopic", "pub", "-1", "/joy_input", "sensor_msgs/Joy",
            json.dumps(joy_message_press)
        ]
        
        # Use Popen for non-blocking execution
        process_press = subprocess.Popen(
            cmd_press, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Wait 200ms asynchronously (doesn't block event loop)
        await asyncio.sleep(0.2)
        
        # Create release message
        joy_message_release = joy_message_press.copy()
        joy_message_release["buttons"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        print("🕺 Dance motion triggered - button released")
        cmd_release = [
            "rostopic", "pub", "-1", "/joy_input", "sensor_msgs/Joy",
            json.dumps(joy_message_release)
        ]
        
        # Send release command (non-blocking)
        process_release = subprocess.Popen(
            cmd_release,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return {
            "tool": "dance_tool",
            "success": True,
            "message": "Dance motion triggered successfully",
            "button_pressed": 0,
            "duration_ms": 200
        }
        
    except FileNotFoundError:
        print("❌ rostopic command not found - is ROS installed and sourced?")
        return {
            "tool": "dance_tool",
            "success": False,
            "error": "rostopic not found - please source ROS environment"
        }
    except Exception as e:
        print(f"❌ Error triggering dance: {e}")
        return {
            "tool": "dance_tool",
            "success": False,
            "error": str(e)
        }


# ============== Session Control Tools ==============

@tool(name="end_session", description="End the current conversation session")
def end_session(farewell_message: str) -> Dict[str, Any]:
    """End the current conversation session and disconnect from the room."""
    
    print("Received end session message. Letting audio play.")
    print(f"👋 {farewell_message}")
    sleeplength = len(farewell_message)/13 + 2 #approximation + buffer
    sleep(sleeplength)
    print("🔌 Disconnecting from LiveKit room...")
    
    # Signal the application to disconnect
    if _app_controller:
        _app_controller.request_disconnect()
    
    return {
        "tool": "end_session",
        "success": True,
        "farewell_message": farewell_message,
        "message": "Session ending, disconnecting from room"
    }