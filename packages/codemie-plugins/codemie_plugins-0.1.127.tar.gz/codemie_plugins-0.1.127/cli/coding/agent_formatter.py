import json
from typing import Any, Dict, Optional, Union

from langchain_core.messages import AIMessage, ToolMessage
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from cli.coding.utils import panel_tool_invocation_result, panel_tool_invoke

# Initialize rich console for pretty terminal output
console = Console()

class AgentResponseFormatter:
    """Class to handle formatting and printing of agent responses using Rich."""

    @staticmethod
    def _format_json(content: Union[str, Dict, Any]) -> Optional[str]:
        """Format content as JSON if possible.
        
        Args:
            content: The content to format as JSON
            
        Returns:
            Formatted JSON string or None if formatting fails
        """
        try:
            if isinstance(content, str):
                parsed_json = json.loads(content)
                return json.dumps(parsed_json, indent=2)
            elif isinstance(content, (dict, list)):
                return json.dumps(content, indent=2)
            return None
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def _format_args(args: Union[str, Dict, Any]) -> str:
        """Format tool arguments for display.
        
        Args:
            args: The arguments to format
            
        Returns:
            Formatted string representation of the arguments
        """
        if isinstance(args, str):
            json_args = AgentResponseFormatter._format_json(args)
            return json_args if json_args else args
        
        try:
            return json.dumps(args, indent=2)
        except Exception:
            return str(args)

    @staticmethod
    def format_tool_message(message: ToolMessage, verbose: bool = False) -> None:
        """Format and print a tool message.
        
        Args:
            message: The tool message to format
            verbose: Whether to show verbose output
        """
        console.print(panel_tool_invocation_result(
            message.name, 
            message.content, 
            status=message.status, 
            verbose=verbose
        ))

    @staticmethod
    def format_ai_message(message: AIMessage) -> None:
        """Format and print an AI message.
        
        Args:
            message: The AI message to format
        """
        # Display message content if present
        if message.content:
            md = Markdown(message.content)
            console.print(Panel(md, title="CodeMie Thoughts", border_style="green"))

        # Handle tool calls if present
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.get('name', 'Unknown Tool')
                args = tool_call.get('args', {})
                args_display = AgentResponseFormatter._format_args(args)
                console.print(panel_tool_invoke(tool_name, args_display))

    @staticmethod
    def _handle_tool_messages(messages: list, verbose: bool = False) -> None:
        """Process and display tool messages.
        
        Args:
            messages: List of tool messages
            verbose: Whether to show verbose output
        """
        for msg in messages:
            AgentResponseFormatter.format_tool_message(msg, verbose=verbose)

    @staticmethod
    def _handle_agent_messages(messages: list) -> None:
        """Process and display agent messages.
        
        Args:
            messages: List of agent messages
        """
        for msg in messages:
            AgentResponseFormatter.format_ai_message(msg)

    @staticmethod
    def _handle_final_output(output: Any) -> None:
        """Format and display final output.
        
        Args:
            output: The output to display
        """

        if isinstance(output, str):
            console.print(Panel(Markdown(output), title="CodeMie Thoughts", border_style="green"))
        else:
            try:
                formatted_output = json.dumps(output, indent=2)
                console.print(Syntax(formatted_output, "json", theme="monokai"))
            except Exception:
                console.print(str(output))

    @staticmethod
    def _handle_error(error_data: Dict[str, Any]) -> None:
        """Format and display error information.
        
        Args:
            error_data: Dictionary containing error information
        """
        error_msg = error_data.get('error', 'Unknown error')
        console.print(Text(f"✗ Error: {error_msg}", style="dim red"))

    @staticmethod
    def _handle_unknown_update(update_type: str, update_data: Dict[str, Any]) -> None:
        """Format and display unknown update types.
        
        Args:
            update_type: The type of update
            update_data: The update data
        """
        console.print(Text(f"ℹ Unknown update type: {update_type}", style="dim yellow"))
        try:
            formatted_data = json.dumps(update_data, indent=2)
            console.print(Syntax(formatted_data, "json", theme="monokai"))
        except Exception:
            console.print(str(update_data))

    @staticmethod
    def print_update(update_type: str, update_data: Dict[str, Any], verbose: bool = False) -> None:
        """Print a formatted update based on its type and content.
        
        Args:
            update_type: The type of update to display
            update_data: The data associated with the update
            verbose: Whether to show verbose output
        """
        # Handle tools update
        if update_type == "tools" and "messages" in update_data:
            AgentResponseFormatter._handle_tool_messages(update_data["messages"], verbose)
        
        # Handle agent update
        elif update_type == "agent" and "messages" in update_data:
            AgentResponseFormatter._handle_agent_messages(update_data["messages"])
        
        # Handle final output
        elif update_type == "final" and "output" in update_data:
            AgentResponseFormatter._handle_final_output(update_data["output"])
        
        # Handle error
        elif update_type == "error":
            AgentResponseFormatter._handle_error(update_data)
        
        # Handle nested updates
        elif update_type == "updates":
            if "tools" in update_data and "messages" in update_data["tools"]:
                AgentResponseFormatter._handle_tool_messages(update_data["tools"]["messages"], verbose)
            elif "agent" in update_data and "messages" in update_data["agent"]:
                AgentResponseFormatter._handle_agent_messages(update_data["agent"]["messages"])
        
        # Handle unknown update types
        else:
            AgentResponseFormatter._handle_unknown_update(update_type, update_data)
