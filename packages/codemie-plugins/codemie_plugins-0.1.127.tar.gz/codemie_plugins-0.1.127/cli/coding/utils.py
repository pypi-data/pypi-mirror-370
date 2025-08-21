import re

from rich.panel import Panel
from rich.json import JSON
from rich.text import Text
import json
from typing import Optional, Any
from rich.console import Group

def pretty_truncate_content(content, verbose, max_lines=10, max_chars=500):
    if verbose:
        if isinstance(content, (dict, list)):
            return JSON.from_data(content)
        else:
            return Text(str(content))
    else:
        if isinstance(content, (dict, list)):
            pretty_str = json.dumps(content, indent=2, ensure_ascii=False)
        else:
            pretty_str = str(content)
        lines = pretty_str.splitlines()
        limited_lines = lines[:max_lines]
        truncated_text = "\n".join(limited_lines)
        if len(truncated_text) > max_chars:
            truncated_text = truncated_text[:max_chars] + "..."
        if len(lines) > max_lines or len(pretty_str) > max_chars:
            truncated_text += "\n\n…truncated, use --verbose to see more"
        return Text(truncated_text)

def panel_tool_invoke(tool_name, args):
    title = f"[bold cyan]Tool: {tool_name}[/]"

    renderables = [
        Text("Args:", style="bold"),
        JSON.from_data(args) if isinstance(args, (dict, list)) else Text(str(args))
        # Removed the "Executing tool..." text to reduce visual noise
    ]
    subtitle = "[blue] Processing … [/]"
    group = Group(*renderables)
    panel = Panel(group, title=title, border_style="blue", subtitle=subtitle)
    return panel

def panel_tool_invocation_result(tool_name, result: Optional[Any]=None, verbose=False, status="success"):
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

    if status == "error":
        renderables.append(Text(f"Error: {result}", style="red bold"))
    else:
        renderables.append(Text("Result:", style="green bold"))
        renderables.append(pretty_truncate_content(result, verbose))

    group = Group(*renderables)
    panel = Panel(group, title=title, border_style=border_style, subtitle=subtitle)
    return panel


def sanitize_string(input_string: str) -> str:
    """
    Sanitize a string by replacing or masking potentially sensitive information.

    This function uses predefined regular expressions to identify and replace common patterns
    of sensitive data such as passwords, usernames, IP addresses, email addresses,
    API keys and credit card numbers.

    Args:
        input_string (str): The original string to be sanitized.

    Returns:
        str: The sanitized string with sensitive information removed or masked.

    Example:
        >>> original_string = "Error: Unable to connect. Username: admin, Password: secret123, IP: 192.168.1.1"
        >>> sanitize_string(original_string)
        'Error: Unable to connect. Username: ***, Password: ***, IP: [IP_ADDRESS]'
    """
    patterns = [
        (r'\b(password|pwd|pass)(\s*[:=]\s*|\s+)(\S+)', r'\1\2***'),  # Passwords
        (r'\b(username|user|uname)(\s*[:=]\s*|\s+)(\S+)', r'\1\2***'),  # Usernames
        (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_ADDRESS]'),  # IP addresses
        (r'\b(?:[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b', '[EMAIL]'),  # Email addresses
        (r'\b(api[_-]?key|access[_-]?token)(\s*[:=]\s*|\s+)(\S+)', r'\1\2[API_KEY]'),  # API keys and access tokens
        (r'\b(?:\d{4}[-\s]?){4}\b', '[CREDIT_CARD]'),  # Credit card numbers
    ]

    sanitized_string = input_string

    for pattern, replacement in patterns:
        sanitized_string = re.sub(pattern, replacement, sanitized_string, flags=re.IGNORECASE)

    return sanitized_string
