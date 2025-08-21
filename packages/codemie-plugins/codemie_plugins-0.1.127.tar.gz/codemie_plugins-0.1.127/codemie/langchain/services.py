# pylint: disable=no-member
import asyncio
import json
import os
import sys
import uuid
from typing import Any, Callable, Optional

import nats
from langchain.tools import BaseTool
from langchain_core.messages import ToolMessage
from nats.errors import FlushTimeoutError
from rich.console import Console, Group
from rich.json import JSON
from rich.panel import Panel
from rich.text import Text
import signal

import codemie.generated.proto.v1.service_pb2 as service_pb2
from codemie.logging import logger

# Initialize console for pretty terminal output
console = Console()


def pretty_truncate_content(content: Any, verbose: bool = False, max_lines: int = 10, max_chars: int = 500) -> Any:
    """
    Format and potentially truncate content for display.
    
    Args:
        content: The content to format
        verbose: Whether to show full content without truncation
        max_lines: Maximum number of lines to show if not verbose
        max_chars: Maximum number of characters to show if not verbose
        
    Returns:
        Formatted content, potentially truncated
    """
    # Handle literal newlines in the string (convert \n to actual newlines)
    if isinstance(content, str) and '\\n' in content and '\n' not in content:
        content = content.replace('\\n', '\n')
        # Handle other common escape sequences
        content = content.replace('\\t', '\t')
        content = content.replace('\\r', '')  # Remove carriage returns
    
    if verbose:
        if isinstance(content, (dict, list)):
            return JSON.from_data(content)
        else:
            return Text(str(content))
    else:
        if isinstance(content, (dict, list)):
            try:
                pretty_str = json.dumps(content, indent=2, ensure_ascii=False)
            except Exception:
                pretty_str = str(content)
        else:
            pretty_str = str(content)
            
        # Add a newline at the beginning for better visual separation if content doesn't start with one
        if pretty_str and not pretty_str.startswith('\n'):
            pretty_str = '\n' + pretty_str
            
        lines = pretty_str.splitlines()
        limited_lines = lines[:max_lines]
        truncated_text = "\n".join(limited_lines)
        if len(truncated_text) > max_chars:
            # Find the last newline before max_chars to keep output clean
            last_newline = truncated_text[:max_chars].rfind('\n')
            if last_newline > 0:
                truncated_text = truncated_text[:last_newline]
            else:
                truncated_text = truncated_text[:max_chars]
            truncated_text += "..."
        if len(lines) > max_lines or len(pretty_str) > max_chars:
            truncated_text += "\n\n…truncated, use VERBOSE=true to see more"
        return Text(truncated_text)


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


class ToolService:
    """Concrete ToolGate service tool implementation."""

    def __init__(self,
        nats_config: dict,
        tool: BaseTool,
        timeout: int = int(os.getenv("PLUGIN_TIMEOUT", "60")),
        prefix: str = None,
        tool_result_converter: Optional[Callable[[ToolMessage], str]] = None
    ):
        self.nats_config = nats_config
        self.tool = tool
        self.prefix = prefix
        self.nc = None
        self.subject = prefix + "." + tool.name
        self.plugin_key = prefix.split(".")[0]
        self.timeout = timeout
        self._running = False
        self._task = None
        self.tool_result_converter = tool_result_converter
        self.nats_max_payload = os.environ.get("NATS_MAX_PAYLOAD", None)


    def serve(self):
        """
        Start serving in the current thread by running the event loop.
        This should only be called if there's no event loop running.
        """
        try:
            asyncio.run(self.a_serve())
        except RuntimeError as e:
            if "already running" in str(e):
                logger.warning("Event loop is already running. Use start() instead of serve().")
                raise RuntimeError("Cannot call serve() from an async context. Use start() instead.")
            raise

    async def start(self):
        """
        Start the service asynchronously and return immediately.
        This should be used when there's already an event loop running.
        """
        if self._task is not None and not self._task.done():
            logger.warning("Service is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self.a_serve())
        return self._task

    async def stop(self):
        """Stop the service gracefully."""
        self._running = False
        if self.nc:
            await self.nc.drain()
            self.nc = None
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def a_serve(self):
        """Serve the tool by subscribing to the NATS server."""
        # Setup signal handlers
        self._setup_signal_handlers()

        try:
            self.nc = await nats.connect(
                servers=self.nats_config["servers"],
                **self.nats_config["options"],
                error_cb=self._on_error,
                disconnected_cb=self._on_disconnect,
                reconnected_cb=self._on_reconnect,
                closed_cb=self._on_close
            )
            if self.nats_max_payload:
                separator = "=" * 50
                logger.print(f"\n{separator}\n[cyan]Setting NATS max payload to {self.nats_max_payload} bytes for tool '{self.tool.name}'[/cyan]\n{separator}")
                self.nc._max_payload = int(self.nats_max_payload)
            await self.subscribe()

            # Replace the infinite loop with a more controlled approach
            while self._running:
                try:
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    logger.print(f"[cyan]Service for tool '{self.tool.name}' was cancelled[/cyan]")
                    break

        except KeyboardInterrupt:
            logger.print(f"[cyan]Received keyboard interrupt. Shutting down tool '{self.tool.name}' gracefully...[/cyan]")
            self._running = False
        except Exception as e:
            separator = "!" * 50
            logger.error(f"\n{separator}\nError in a_serve for tool '{self.tool.name}': {str(e)}\n{separator}")
            self._running = False
            raise
        finally:
            try:
                if self.nc:
                    logger.print(f"[cyan]Draining NATS connection for tool '{self.tool.name}'...[/cyan]")
                    await self.nc.drain()
                    self.nc = None
                    logger.print(f"[cyan]NATS connection drained for tool '{self.tool.name}'[/cyan]")
            except FlushTimeoutError:
                pass
            except Exception as e:
                logger.error(f"Error during cleanup for tool '{self.tool.name}': {str(e)}")

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()

        # Define signal handler for asyncio
        def signal_handler():
            logger.print(f"[cyan]Received termination signal. Initiating graceful shutdown for tool '{self.tool.name}'...[/cyan]")
            self._running = False

            # Cancel all running tasks except the current one
            for task in asyncio.all_tasks(loop):
                if task is not asyncio.current_task():
                    task.cancel()

        if sys.platform == "win32":
            # On Windows, use signal.signal and schedule shutdown on the event loop
            def win_handler(signum, frame):
                loop.call_soon_threadsafe(signal_handler)
            for sig in [signal.SIGINT, signal.SIGTERM]:
                try:
                    signal.signal(sig, win_handler)
                except Exception as e:
                    logger.error(f"Could not set signal handler for {sig}: {e}")
        else:
            # On UNIX, use loop.add_signal_handler
            for sig in [signal.SIGINT, signal.SIGTERM]:
                try:
                    loop.add_signal_handler(sig, signal_handler)
                except Exception as e:
                    logger.error(f"Could not add signal handler for {sig}: {e}")

        # Add callback handlers for NATS connection events
    async def _on_error(self, e):
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"NATS error for tool '{self.tool.name}': {str(e)}\n{error_trace}")

    async def _on_disconnect(self):
        logger.warning(f"NATS disconnected for tool '{self.tool.name}'")

    async def _on_reconnect(self):
        logger.print(f"[cyan]NATS reconnected for tool '{self.tool.name}'[/cyan]")

    async def _on_close(self):
        logger.print(f"[cyan]NATS connection closed for tool '{self.tool.name}'[/cyan]")
        self._running = False

    async def execute_tool_with_timeout(self, query, timeout):
        error_message = "Call to the tool timed out."
        try:
            tool_input = json.loads(query)
            tool_response = await asyncio.wait_for(
                self.tool.arun(tool_input, tool_call_id=str(uuid.uuid4())), timeout
            )
            logger.info(format_tool_message(self.tool.name, tool_input, tool_response))
            return tool_response

        except asyncio.TimeoutError:
            separator = "!" * 50
            error_msg = f"\n{separator}\nTool '{self.tool.name}' operation timed out after {timeout} seconds\n{separator}"
            logger.error(error_msg)
            return error_message
        except json.JSONDecodeError:
            separator = "!" * 50
            error_msg = f"\n{separator}\nTool '{self.tool.name}' failed to decode JSON input\n{separator}"
            logger.error(error_msg)
            return "Failed to decode JSON input."
        except Exception as e:
            separator = "!" * 50
            error_msg = f"\n{separator}\nTool '{self.tool.name}' error: {e}\n{separator}"
            logger.error(error_msg)
            return f"An error occurred: {e}"

    async def subscribe(self):
        """Subscribe to the service subject and run handlers."""

        async def _info_handler(msg):
            logger.debug("Running tool handler %s", self.tool.name)
            response = service_pb2.ServiceResponse()
            response.meta.subject = self.subject
            response.meta.handler = service_pb2.Handler.GET
            response.meta.puppet = service_pb2.Puppet.LANGCHAIN_TOOL
            response.puppet_response.lc_tool.name = self.tool.name
            response.puppet_response.lc_tool.description = self.tool.description
            # Handle both dict and BaseModel cases
            if hasattr(self.tool.args_schema, 'model_json_schema'):
                args_schema_json = json.dumps(self.tool.args_schema.model_json_schema())
            elif isinstance(self.tool.args_schema, dict):
                args_schema_json = json.dumps(self.tool.args_schema)
            else:
                args_schema_json = None
            response.puppet_response.lc_tool.args_schema = args_schema_json
            await self.nc.publish(msg.reply, response.SerializeToString())

        async def _run_handler(msg, query: str = None):
            response = service_pb2.ServiceResponse()
            response.meta.subject = self.subject
            response.meta.handler = service_pb2.Handler.RUN
            response.meta.puppet = service_pb2.Puppet.LANGCHAIN_TOOL
            try:
                tool_response = await self.execute_tool_with_timeout(query, self.timeout)
                converted_response = (
                    self.tool_result_converter(tool_response) if self.tool_result_converter else str(tool_response)
                )
                response.puppet_response.lc_tool.result = converted_response

            except Exception as exc:
                separator = "!" * 50
                error_message = f"Tool '{self.tool.name}' got error: {exc}"
                logger.error(f"\n{separator}\n{error_message}\n{separator}", exc_info=True)
                response.puppet_response.lc_tool.error = error_message

            await self.nc.publish(msg.reply, response.SerializeToString())
        
        async def _subject_discovery_handler(msg):
            await self.nc.publish(msg.reply, self.subject.encode())

        async def _main_handler(msg):
            logger.debug("Running main handler for message: %s", msg.data)
            request = service_pb2.ServiceRequest()
            request.ParseFromString(msg.data)
            if request.IsInitialized():
                if (
                    request.meta.subject == self.subject
                    and request.meta.handler == service_pb2.Handler.GET
                    and request.meta.puppet == service_pb2.Puppet.LANGCHAIN_TOOL
                ):
                    await _info_handler(msg)
                elif (
                    request.meta.subject == self.subject
                    and request.meta.handler == service_pb2.Handler.RUN
                    and request.meta.puppet == service_pb2.Puppet.LANGCHAIN_TOOL
                ):
                    await _run_handler(msg, query=request.puppet_request.lc_tool.query)

        sub = await self.nc.subscribe(self.subject, cb=_main_handler)
        await self.nc.subscribe(self.plugin_key + "." + "ping", cb=_subject_discovery_handler)

        if sub:
            logger.print(f"[cyan]Tool '{self.tool.name}' subscribed to subject: {self.subject}[/cyan]")
        while True:
            await asyncio.sleep(1)

    def tool_metadata_dict(self):
        """Return a dictionary representation of the tool metadata."""

        return {
            "name": self.tool.name,
            "description": self.tool.description,
            "args_schema": (
                self.tool.args_schema.schema() if self.tool.args_schema else None
            ),
        }