
from typing_extensions import Any

from agentlin.code_interpreter.types import MIME_TOOL_CALL, MIME_TOOL_RESPONSE, ToolCall, ToolResponse


class MimeDisplayObject:
    """Display wrapper for ToolCall objects"""
    def __init__(self, mime_type: str, data: dict):
        self.mime_type = mime_type
        self.data = data

    def _repr_mimebundle_(self, include=None, exclude=None):
        return {
            self.mime_type: self.data,
            # 'text/plain': f"{json.dumps(self.data, indent=2, ensure_ascii=False)}"
        }


# Try to import IPython components and check if we're in an IPython environment
try:
    from IPython.display import display as ipython_display
    from IPython.core.display import DisplayObject
    from IPython import get_ipython

    # Check if we're actually running in an IPython environment
    if get_ipython() is not None:
        display = ipython_display
        IPYTHON_AVAILABLE = True
    else:
        # IPython is installed but we're not in an IPython environment
        raise ImportError("Not in IPython environment")

except (ImportError, AttributeError):
    # Create dummy classes for non-IPython environments
    class DisplayObject:
        def __init__(self, data=None, metadata=None, **kwargs):
            self.data = data or {}
            self.metadata = metadata or {}

        def _repr_mimebundle_(self, include=None, exclude=None):
            return self.data

    class MimeBundle(DisplayObject):
        """A display object that wraps a MIME bundle dictionary"""
        def __init__(self, data_dict):
            if isinstance(data_dict, dict):
                super().__init__(data=data_dict)
            else:
                super().__init__(data={'text/plain': str(data_dict)})

    def display(obj):
        """Fallback display function for non-IPython environments"""
        # Handle our custom display objects first
        if hasattr(obj, '_repr_mimebundle_'):
            bundle = obj._repr_mimebundle_()
        elif isinstance(obj, dict):
            # Handle MIME bundle dictionary directly
            bundle = obj
        else:
            bundle = {'text/plain': str(obj)}

        # Display the content based on available MIME types
        if MIME_TOOL_CALL in bundle:
            tool_call_data = bundle[MIME_TOOL_CALL]
            print(f"🔧 Tool Call: {tool_call_data.get('tool_name', 'Unknown')} (ID: {tool_call_data.get('call_id', 'N/A')})")
            if tool_call_data.get('tool_args'):
                print(f"   Arguments: {tool_call_data['tool_args']}")
        elif MIME_TOOL_RESPONSE in bundle:
            tool_response_data = bundle[MIME_TOOL_RESPONSE]
            blocks = tool_response_data.get('block_list', [])
            content = tool_response_data.get('message_content', [])
            print(f"📤 Tool Response: {len(blocks)} blocks, {len(content)} content items")
            if blocks:
                for i, block in enumerate(blocks[:3]):  # Show first 3 blocks
                    block_type = block.get('type', 'unknown')
                    print(f"   Block {i+1}: {block_type}")
                if len(blocks) > 3:
                    print(f"   ... and {len(blocks) - 3} more blocks")
        elif 'text/html' in bundle:
            print(f"HTML: {bundle['text/html']}")
        elif 'text/markdown' in bundle:
            print(f"Markdown: {bundle['text/markdown']}")
        elif 'application/json' in bundle:
            import json
            print(f"JSON: {json.dumps(bundle['application/json'], indent=2)}")
        elif 'text/plain' in bundle:
            print(bundle['text/plain'])
        else:
            # Fallback to string representation
            print(str(bundle))

    IPYTHON_AVAILABLE = False


def display_tool_response(
    message_content: list[dict[str, Any]],
    block_list: list[dict[str, Any]],
    **kwargs,
):
    """
    Display tool response data in Jupyter notebook

    Args:
        message_content: List of dictionaries containing tool response data
        block_list: List of dictionaries containing block information
        **kwargs: Additional keyword arguments
    """
    tool_response = ToolResponse(
        message_content=message_content,
        block_list=block_list,
        data=kwargs,
    )

    # Create display object that supports _repr_mimebundle_
    display_obj = MimeDisplayObject(MIME_TOOL_RESPONSE, tool_response)
    display(display_obj)


def display_tool_call(
    tool_name: str,
    tool_args: dict[str, Any],
    call_id: str,
):
    """
    Display tool call information in Jupyter notebook

    Args:
        tool_name: Name of the tool being called
        tool_args: Arguments passed to the tool
        call_id: Unique identifier for the tool call
    """
    tool_call = ToolCall(
        type="tool_call",
        tool_name=tool_name,
        tool_args=tool_args,
        call_id=call_id,
    )

    # Create display object that supports _repr_mimebundle_
    display_obj = MimeDisplayObject(MIME_TOOL_CALL, tool_call)
    display(display_obj)