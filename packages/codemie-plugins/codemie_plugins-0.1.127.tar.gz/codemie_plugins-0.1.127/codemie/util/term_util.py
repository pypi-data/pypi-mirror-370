from typing import Any, Optional
import json
import os
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text


console = Console()


def format_tool_message(
        tool_name: str,
        tool_input: Any,
        content: Any,
        max_length: Optional[int] = 300
) -> str:
    """Format and truncate tool input and output for logging in a single message.

    Args:
        tool_name: Name of the tool
        tool_input: The input to the tool
        content: The output from the tool
        max_length: Maximum length of the formatted content

    Returns:
        Formatted and potentially truncated string with both input and output
    """
    # Skip truncation if in verbose mode
    verbose = os.environ.get('VERBOSE', 'false').lower()
    if verbose == 'true':
        max_length = None

    # For input, convert to JSON if possible
    if isinstance(tool_input, dict):
        try:
            input_str = json.dumps(tool_input, indent=2)
        except json.JSONDecodeError:
            input_str = str(tool_input)
    else:
        input_str = str(tool_input)

    # Format the input content
    formatted_input = format_tool_content(
        input_str,
        max_length=max_length
    )

    # Format the output content
    formatted_output = format_tool_content(
        content,
        max_length=max_length
    )
    # Create a rich panel for display
    panel = create_tool_panel(tool_name, formatted_input, formatted_output)

    # Use the Rich console for display
    console.print(panel)

    # Return empty string since we've already printed with console.print
    return ""


def create_tool_panel(tool_name: str, tool_input: Any, content: Any, status: str = "success") -> Panel:
    """
    Create a rich panel for tool invocation and result.

    Args:
        tool_name: Name of the tool
        tool_input: Input provided to the tool
        content: Result from the tool
        status: Status of the tool execution (success or error)

    Returns:
        Rich Panel object for display
    """
    # Determine styling based on status
    if status == "error":
        border_style = "red"
        status_icon = "✗"
        status_text = "Failed"
        status_style = "red"
    else:
        border_style = "green"
        status_icon = "✓"
        status_text = "Completed"
        status_style = "green"

    title = f"[bold cyan]Tool: {tool_name}[/]"
    subtitle = f"[{status_style}]{status_icon} {status_text}[/{status_style}]"

    renderables = []

    # Format input
    renderables.append(Text("Args:", style="bold"))
    renderables.append(tool_input)

    # Add separator
    renderables.append(Text("\n" + "-" * 40))

    # Format result
    if status == "error":
        renderables.append(Text("Error:", style="red bold"))
        renderables.append(Text(str(content), style="red"))
    else:
        renderables.append(Text("Result:", style="green bold"))
        renderables.append(content)

    group = Group(*renderables)
    return Panel(group, title=title, border_style=border_style, subtitle=subtitle)


def format_tool_content(content: Any, max_length: Optional[int], is_json: bool = True) -> str:
    """Format and truncate content for logging.

    Args:
        content: The content to format
        max_length: Maximum length of the formatted content
        is_json: Whether to try parsing as JSON

    Returns:
        Formatted and potentially truncated string
    """
    # Convert to string if it's not already
    content_str = str(content)

    # Handle literal newlines in the string (convert \\n to actual newlines)
    if '\\n' in content_str and '\n' not in content_str:
        content_str = content_str.replace('\\n', '\n')

    # Handle other common escape sequences
    content_str = content_str.replace('\\t', '\t')
    content_str = content_str.replace('\\r', '')  # Remove carriage returns

    # For JSON-like content, try to pretty print it
    if is_json and ((content_str.startswith('{') and content_str.endswith('}')) or
                    (content_str.startswith('[') and content_str.endswith(']'))):
        try:
            # Try to parse and pretty print JSON
            parsed = json.loads(content_str)
            # Use a more readable JSON format with indentation and sorted keys
            content_str = json.dumps(parsed, indent=2, sort_keys=True)
        except json.JSONDecodeError:
            # Not valid JSON, continue with original string
            pass

    # Add a newline at the beginning for better visual separation if content doesn't start with one
    if content_str and not content_str.startswith('\n'):
        content_str = '\n' + content_str

    # Truncate if too long
    if max_length and len(content_str) > max_length:
        # Find the last newline before max_length to keep output clean
        last_newline = content_str[:max_length].rfind('\n')
        if last_newline > 0:
            truncated = content_str[:last_newline]
        else:
            truncated = content_str[:max_length]

        truncation_msg = f"\n\n[...TRUNCATED... full content length: {len(content_str)} chars]"
        return f"{truncated}{truncation_msg}"

    return content_str
