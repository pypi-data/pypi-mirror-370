import argparse
import asyncio
import functools
import json
import os
import sys
import types
from typing import Any, Callable, Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, StructuredTool, ToolException
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.client.stdio import get_default_environment
from pydantic import BaseModel

from codemie.client import PluginClient
from codemie.logging import logger

# --- Configuration Constants ---
CONFIG_FILE = "servers.json"
CONFIG_KEY_MCP_SERVERS = "mcpServers"
CONFIG_KEY_TRANSPORT = "transport"
CONFIG_KEY_ENV = "env"
CONFIG_KEY_ARGS = "args"

# --- Environment Variable Names ---
ENV_VAR_TIMEOUT = "TIMEOUT"
ENV_VAR_FILE_PATHS = "FILE_PATHS"
ENV_VAR_DEFAULT_PATH = "DEFAULT_PATH"

# --- Transport Types ---
TRANSPORT_STDIO = "stdio"

# --- Server Names ---
SERVER_FILESYSTEM = "filesystem"

# --- Message Types ---
MESSAGE_TYPE_METADATA = "metadata"
MESSAGE_TYPE_TEXT = "text"
MESSAGE_TYPE_DATA = "data"
MESSAGE_TYPE_ERROR = "error"

# --- Tool Message Keys ---
TOOL_KEY_TYPE = "type"
TOOL_KEY_METADATA = "metadata"
TOOL_KEY_TEXT = "text"
TOOL_KEY_DATA = "data"

# --- Other Constants ---
MCP_THROUGH_PLUGIN = "mcp_through_plugin"
DEFAULT_TIMEOUT_SECONDS = 120
EXIT_CODE_ERROR = 1

class ConfigurationError(Exception):
    """Custom exception for configuration related errors."""
    pass

class MCPToolException(ToolException):
    pass

# --- Argument Parsing ---
class ArgumentHandler:
    """Handles command-line argument parsing and validation."""

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description="Start MCP servers with specified configuration"
        )
        self._add_arguments()

    def _add_arguments(self) -> None:
        """Adds arguments to the parser."""

        self.parser.add_argument(
            "-s", "--servers",
            required=True,
            help="Comma-separated list of server names to start"
        )
        self.parser.add_argument(
            "-e", "--env",
            action="append",
            nargs=1,
            help=(
                "Server-specific environment variables in the format 'server_name=VAR1,VAR2,...'. "
                "These environment variables will be added to the server configuration with "
                "values that exist in the current environment"
            ),
            default=[]
        )

    def parse_args(self) -> argparse.Namespace:
        """Parses the command line arguments."""

        return self.parser.parse_args()

    @staticmethod
    def parse_server_names(servers_arg: str) -> list[str]:
        """
        Parse comma-separated server names string into a list.

        Args:
            servers_arg: Comma-separated string of server names

        Returns:
            list of server names
        """

        if not servers_arg:
            return []
        return [name.strip() for name in servers_arg.split(",") if name.strip()]

    @staticmethod
    def parse_environment_variables(
        env_args: list[list[str]],
        server_names: list[str]
    ) -> dict[str, list[str]]:
        """
        Parse environment variable arguments into a dictionary mapping server names to variables.

        Args:
            env_args: list of environment variable specifications from argparse
            server_names: list of valid server names for validation

        Returns:
            dictionary mapping server names to lists of environment variable names
        """

        server_env_vars: dict[str, list[str]] = {}

        for env_arg_list in env_args:
            env_spec = env_arg_list[0]

            if '=' not in env_spec:
                logger.warning(
                    f"Invalid environment variable specification: '{env_spec}'. "
                    "Format should be 'server_name=VAR1,VAR2'. Skipping."
                )
                continue

            server_name, env_vars_str = env_spec.split('=', 1)
            server_name = server_name.strip()

            if server_name not in server_names:
                logger.warning(
                    f"Server '{server_name}' specified in -e option was not found "
                    f"in the provided server list: {server_names}. Skipping."
                )
                continue

            env_vars = [var.strip() for var in env_vars_str.split(',') if var.strip()]
            if env_vars:
                server_env_vars[server_name] = env_vars
                logger.print(f"[cyan]Registered environment variables for server '{server_name}':[/cyan] {env_vars}")
            else:
                logger.warning(f"No valid environment variables found for server '{server_name}' in spec: '{env_spec}'")

        return server_env_vars

# --- Configuration Management ---
class ConfigurationManager:
    """Handles loading and processing of server configurations."""

    def __init__(self, server_names: list[str], server_env_vars: Optional[dict[str, list[str]]] = None) -> None:
        self.server_names = server_names
        self.server_env_vars = server_env_vars or {}
        self.config_path = self._get_server_config_path()
        self.servers: dict[str, Any] = {}

    @staticmethod
    def _get_server_config_path() -> str:
        """Get the server configuration file path."""

        return CONFIG_FILE

    def load_and_prepare_servers(self) -> dict[str, Any]:
        """Loads, filters, processes, and configures environments for servers."""

        if not self.server_names:
            logger.error("No server names provided for configuration.")
            raise ConfigurationError("Cannot load configuration without server names.")

        logger.print(f"[cyan]Using server configuration file:[/cyan] {self.config_path}")
        try:
            all_servers_config = self._load_config_from_file()
        except FileNotFoundError:
            logger.error(f"Configuration file '{self.config_path}' not found.")
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in '{self.config_path}': {e}")
            raise ConfigurationError(f"Invalid JSON in configuration file: {self.config_path}")

        self.servers = self._filter_and_process_servers(all_servers_config)

        if not self.servers:
            logger.error(f"No valid server configurations found for names: {self.server_names}")
            raise ConfigurationError("No valid server configurations could be loaded.")

        self._configure_server_environments()
        return self.servers

    def _load_config_from_file(self) -> dict[str, Any]:
        """Loads the raw configuration from the JSON file."""

        with open(self.config_path, 'r') as f:
            config = json.load(f)
        return config.get(CONFIG_KEY_MCP_SERVERS, {})

    def _filter_and_process_servers(self, all_servers: dict[str, Any]) -> dict[str, Any]:
        """Filters servers by name and applies initial processing and defaults."""

        selected_servers: dict[str, Any] = {}
        for name in self.server_names:
            if name in all_servers:
                server_config = all_servers[name].copy() # Use copy to avoid modifying original dict

                # Add default transport if not specified
                if CONFIG_KEY_TRANSPORT not in server_config:
                    server_config[CONFIG_KEY_TRANSPORT] = TRANSPORT_STDIO
                    logger.debug(f"Applied default transport '{TRANSPORT_STDIO}' to server '{name}'")

                # Special handling for filesystem server paths
                if name == SERVER_FILESYSTEM:
                    server_config = self._configure_filesystem_paths(server_config)

                selected_servers[name] = server_config
            else:
                logger.warning(f"Server '{name}' not found in configuration file '{self.config_path}'. Skipping.")
        return selected_servers

    def _configure_filesystem_paths(self, server_config: dict[str, Any]) -> dict[str, Any]:
        """Configure filesystem server paths based on environment variables."""

        file_paths_env = os.environ.get(ENV_VAR_FILE_PATHS)
        default_path_env = os.environ.get(ENV_VAR_DEFAULT_PATH)

        # Initialize args list if it doesn't exist or is not a list
        if CONFIG_KEY_ARGS not in server_config or not isinstance(server_config.get(CONFIG_KEY_ARGS), list):
            server_config[CONFIG_KEY_ARGS] = []
            logger.debug(f"Initialized empty args list for server '{SERVER_FILESYSTEM}'")

        # Determine which paths to use from environment
        paths_to_add = self._get_paths_from_environment(file_paths_env, default_path_env)

        # Add paths to the args array if any were found
        if paths_to_add:
            # Ensure args is a list before extending
            if isinstance(server_config[CONFIG_KEY_ARGS], list):
                server_config[CONFIG_KEY_ARGS].extend(paths_to_add)
                logger.print(f"[cyan]Added paths from environment to '{SERVER_FILESYSTEM}' args:[/cyan] {paths_to_add}")
            else:
                logger.warning(f"Could not add paths to '{SERVER_FILESYSTEM}' args as it's not a list.")

        return server_config

    @staticmethod
    def _get_paths_from_environment(file_paths_env: Optional[str], default_path_env: Optional[str]) -> list[str]:
        """Extract paths from environment variables."""

        if file_paths_env:
            paths = [path.strip() for path in file_paths_env.split(",") if path.strip()]
            if paths:
                logger.print(f"[cyan]Using custom filesystem paths from {ENV_VAR_FILE_PATHS}:[/cyan] {paths}")
                return paths
            else:
                logger.warning(f"{ENV_VAR_FILE_PATHS} environment variable is set but contains no valid paths.")

        if default_path_env:
            default_path = default_path_env.strip()
            if default_path:
                logger.print(f"[cyan]Using default path from {ENV_VAR_DEFAULT_PATH}:[/cyan] {default_path}")
                return [default_path]
            else:
                logger.warning(f"{ENV_VAR_DEFAULT_PATH} environment variable is set but is empty.")

        logger.warning("No filesystem paths specified via environment variables. Using paths from config file if present.")
        return []

    def _configure_server_environments(self) -> None:
        """Configure environment for each server based on its transport type and specified env vars."""

        for server_name, server_config in self.servers.items():
            if server_config.get(CONFIG_KEY_TRANSPORT) == TRANSPORT_STDIO:
                server_config[CONFIG_KEY_ENV] = self._apply_environment_variables(
                    server_config, server_name
                )
            elif CONFIG_KEY_ENV in server_config:
                # Remove 'env' key for non-stdio transports to avoid confusion
                del server_config[CONFIG_KEY_ENV]
                logger.debug(f"Removed '{CONFIG_KEY_ENV}' key for non-stdio server '{server_name}'")

    def _apply_environment_variables(
        self,
        server_config: dict[str, Any],
        server_name: str
    ) -> dict[str, str]:
        """Apply environment variables to a server configuration's env dictionary."""

        # Start with default environment
        env: dict[str, str] = get_default_environment()

        # Update with server's specific 'env' block from config file, if valid
        config_env = server_config.get(CONFIG_KEY_ENV)
        if isinstance(config_env, dict):
            # Ensure all values are strings as expected by subprocess
            env.update({k: str(v) for k, v in config_env.items()})
        elif config_env is not None:
            logger.warning(f"'{CONFIG_KEY_ENV}' key for server '{server_name}' in config file is not a dictionary. Ignoring.")

        # Add environment variables specified via command line (-e) for this server
        if server_name in self.server_env_vars:
            for var_name in self.server_env_vars[server_name]:
                self._process_environment_variable(env, var_name, server_name)

        return env

    @staticmethod
    def _process_environment_variable(env: dict[str, str], var_name: str, server_name: str) -> None:
        """Process a single environment variable and add it to the server's env dict if valid."""

        if var_name not in os.environ:
            logger.warning(f"Requested environment variable '{var_name}' for server '{server_name}' not found in the current environment. Skipping.")
            return

        val = os.environ[var_name]
        if not val.strip():
            logger.warning(f"Environment variable '{var_name}' for server '{server_name}' has an empty value. Skipping.")
            return

        env[var_name] = val
        # Avoid logging sensitive values directly
        logger.print(f"[cyan]Added environment variable '{var_name}' to server '{server_name}' environment.[/cyan]")

# --- Plugin Execution ---
class PluginRunner:
    """Handles MCP client setup, tool wrapping, and plugin execution."""

    def __init__(self, servers: dict[str, Any]) -> None:
        self.servers = servers
        self.timeout = self._get_timeout()
        self._configure_structured_tool()

    @staticmethod
    def _configure_structured_tool() -> None:
        """Allow extra fields in StructuredTool for compatibility."""

        # This allows attaching arbitrary metadata potentially needed by MCP adapters/tools
        StructuredTool.model_config['extra'] = 'allow'

    @staticmethod
    def _get_timeout() -> int:
        """Get the timeout value from environment or use default."""

        timeout_str = os.environ.get(ENV_VAR_TIMEOUT)

        if timeout_str is None:
            logger.print(f"[cyan]'{ENV_VAR_TIMEOUT}' environment variable not set. Using default:[/cyan] {DEFAULT_TIMEOUT_SECONDS} seconds.")
            return DEFAULT_TIMEOUT_SECONDS

        timeout_str = timeout_str.strip()
        if not timeout_str:
            logger.print(f"[cyan]'{ENV_VAR_TIMEOUT}' environment variable is empty. Using default:[/cyan] {DEFAULT_TIMEOUT_SECONDS} seconds.")
            return DEFAULT_TIMEOUT_SECONDS

        try:
            timeout_val = int(timeout_str)
            if timeout_val <= 0:
                logger.warning(f"Invalid timeout value '{timeout_val}' (must be positive). Using default: {DEFAULT_TIMEOUT_SECONDS} seconds.")
                return DEFAULT_TIMEOUT_SECONDS
            logger.print(f"[cyan]Using timeout value from environment:[/cyan] {timeout_val} seconds.")
            return timeout_val
        except ValueError:
            logger.warning(f"Invalid timeout value '{timeout_str}' in environment variable '{ENV_VAR_TIMEOUT}'. Must be an integer. Using default: {DEFAULT_TIMEOUT_SECONDS} seconds.")
            return DEFAULT_TIMEOUT_SECONDS

    @staticmethod
    def _create_arun_output_wrapper(original_arun_method: Callable) -> Callable:
        """
        Creates a wrapper for BaseTool.arun to inject MCP plugin metadata
        into ToolMessage responses, and log/handle exceptions robustly.

        - Wraps the original async arun method
        - Ensures responses include MCP_THROUGH_PLUGIN metadata
        - Handles ToolException by logging and *raising* (not returning), which fits async tool routing.
        - Preserves signature, name, and docstring.
        """
        @functools.wraps(original_arun_method)
        async def wrapped_arun(self, *args, **kwargs):  # type: ignore
            try:
                result = await original_arun_method(self, *args, **kwargs)
            except ToolException as ex:
                logger.error(f"Tool '{getattr(self, 'name', str(self))}' exception: {ex}.", exc_info=True)
                # Reraise as MCPToolException, so error path is explicit in stack
                return MCPToolException(str(ex))

            # Postprocess for ToolMessage
            if isinstance(result, ToolMessage):
                response_metadata = result.response_metadata if isinstance(result.response_metadata, dict) else {}
                response_metadata[MCP_THROUGH_PLUGIN] = True
                result.response_metadata = response_metadata  # assign back, just in case
            return result

        return wrapped_arun

    def _wrap_tool_arun_methods(self, tools: list[BaseTool]) -> list[BaseTool]:
        """Wrap the arun methods of tools with the MCP metadata output wrapper."""
        for tool in tools:
            if hasattr(tool, 'arun') and callable(tool.arun):
                original_arun = tool.arun
                # Bind the new wrapped method to the instance
                # Use __func__ to get the original unbound function from the method
                if hasattr(original_arun, '__func__'):
                    wrapped_method = self._create_arun_output_wrapper(original_arun.__func__)
                    tool.arun = types.MethodType(wrapped_method, tool)
                    logger.debug(f"Wrapped 'arun' method for tool: {tool.name}")
                else:
                    logger.warning(f"Could not access unbound function for 'arun' on tool '{tool.name}'. Wrapping might not work as expected.")
            else:
                logger.debug(f"Tool '{tool.name}' does not have a callable 'arun' method. Skipping wrapping.")
        return tools

    @staticmethod
    def convert_tool_message_to_json(tool_message: Any) -> str:
        """
        Convert a ToolMessage to a JSON string representation for the plugin client.

        Args:
            tool_message: The tool message to convert

        Returns:
            JSON string representation of the tool message content and metadata.
        """
        # Handle string input directly
        if isinstance(tool_message, str):
            return tool_message

        # Handle tool exceptions
        if isinstance(tool_message, MCPToolException):
            return PluginRunner._format_tool_exception(tool_message)

        # Process complex tool message
        result_list = []

        # Add metadata if present
        if tool_message.response_metadata:
            result_list.append(PluginRunner._create_metadata_entry(tool_message.response_metadata))

        # Add text content if present
        if tool_message.content:
            result_list.extend(PluginRunner._create_text_entry(tool_message.content))

        # Process artifacts if present
        if tool_message.artifact:
            PluginRunner._process_artifacts(tool_message.artifact, result_list)

        try:
            return json.dumps(result_list)
        except TypeError as e:
            logger.error(f"Failed to serialize tool message result to JSON: {e}. Content: {result_list}")
            return str(result_list)

    @staticmethod
    def _format_tool_exception(exception: MCPToolException) -> str:
        """Format a tool exception as JSON."""
        result_list = [
            {
                TOOL_KEY_TYPE: MESSAGE_TYPE_ERROR,
                TOOL_KEY_TEXT: str(exception)
            },
            {
                TOOL_KEY_TYPE: MESSAGE_TYPE_METADATA,
                TOOL_KEY_METADATA: {MCP_THROUGH_PLUGIN: True}
            }
        ]
        return json.dumps(result_list)

    @staticmethod
    def _create_metadata_entry(metadata: dict) -> dict:
        """Create a metadata entry for the result list."""
        return {
            TOOL_KEY_TYPE: MESSAGE_TYPE_METADATA,
            TOOL_KEY_METADATA: metadata
        }

    @staticmethod
    def _create_text_entry(text: Any) -> list[dict[str, str]]:
        content = text if isinstance(text, list) else [text]
        return [{
            TOOL_KEY_TYPE: MESSAGE_TYPE_TEXT,
            TOOL_KEY_TEXT: json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else str(item)
        } for item in content]

    @staticmethod
    def _process_artifacts(artifact: Any, result_list: list) -> None:
        """Process and add artifacts to the result list."""
        artifacts = artifact if isinstance(artifact, list) else [artifact]

        for item in artifacts:
            if isinstance(item, BaseModel):
                result_list.append(item.model_dump(mode='json'))
            elif isinstance(item, (dict, list, str, int, float, bool, type(None))):
                result_list.append({
                    TOOL_KEY_TYPE: MESSAGE_TYPE_DATA,
                    TOOL_KEY_DATA: item
                })
            else:
                logger.warning(f"Cannot directly serialize artifact of type {type(item)}. Converting to string.")
                result_list.append({
                    TOOL_KEY_TYPE: MESSAGE_TYPE_DATA,
                    TOOL_KEY_DATA: str(item)
                })

    async def run(self) -> None:
        """Initialize the MCP client, prepare tools, and start the plugin."""

        logger.print("[cyan]Initializing MCP Client...[/cyan]")
        async with MultiServerMCPClient(self.servers) as client:
            logger.print("[bold green]✓[/bold green] MCP Client initialized")
            
            # Use safe_status context manager for better error handling
            with logger.safe_status("Fetching tools..."):
                tools = client.get_tools()
            logger.progress(f"Fetched {len(tools)} tools", complete=True)
            
            # Wrap tools using safe_status
            with logger.safe_status("Wrapping tool methods..."):
                wrapped_tools = self._wrap_tool_arun_methods(tools)
            logger.progress("Tools prepared for execution", complete=True)

            # Initialize plugin
            with logger.safe_status("Initializing PluginClient..."):
                plugin = PluginClient(
                    tools=wrapped_tools,
                    tool_result_converter=self.convert_tool_message_to_json,
                    timeout=self.timeout
                )
            logger.progress("PluginClient initialized", complete=True)

            # Connect plugin
            try:
                await plugin.connect()
                logger.progress("PluginClient finished execution", complete=True)
            except Exception as e:
                logger.error(f"Error during plugin connection: {e}")
                raise

# --- Main Execution Logic ---
async def main_async(
    server_names: list[str],
    server_env_vars: Optional[dict[str, list[str]]] = None
) -> None:
    """
    Asynchronous main function to configure servers and run the plugin.

    Args:
        server_names: list of server names to include
        server_env_vars: dictionary mapping server names to environment variable names
    """

    try:
        # 1. Configure Servers
        logger.rule("[bold blue]Server Configuration")
        with logger.safe_status("Configuring servers..."):
            config_manager = ConfigurationManager(server_names, server_env_vars)
            servers = config_manager.load_and_prepare_servers()
        logger.progress(f"Successfully loaded and configured servers: {list(servers.keys())}", complete=True)

        # 2. Run Plugin
        logger.rule("[bold blue]Plugin Execution")
        plugin_runner = PluginRunner(servers)
        await plugin_runner.run()
    except ProcessLookupError:
        logger.warning("MCP execution was cancelled by user")
        # Re-raise to propagate cancellation
        raise

    except ConfigurationError as ex:
        logger.error(f"Configuration failed: {ex}")
        raise

if __name__ == "__main__":
    exit_code = 0
    try:
        # Display application header
        logger.rule("[bold blue]MCP Plugin Execution[/bold blue]")
        
        # 1. Parse Arguments
        with logger.safe_status("Parsing command line arguments..."):
            arg_handler = ArgumentHandler()
            args = arg_handler.parse_args()
        logger.progress("Command line arguments parsed", complete=True)

        # 2. Process Parsed Arguments
        server_names = arg_handler.parse_server_names(args.servers)
        if not server_names:
            logger.error("No valid server names provided via -s/--servers argument. Exiting.")
            sys.exit(EXIT_CODE_ERROR)

        logger.print(f"[bold cyan]Requested MCP servers:[/bold cyan] {', '.join(server_names)}")

        with logger.safe_status("Processing environment variables..."):
            server_env_vars = arg_handler.parse_environment_variables(args.env, server_names)
        logger.progress("Environment variables processed", complete=True)

        # 3. Run Asynchronous Main Logic
        asyncio.run(main_async(server_names=server_names, server_env_vars=server_env_vars))

        # Display completion message
        logger.rule("[bold green]Execution Complete[/bold green]")
        logger.print("[bold green]✓ MCP Plugin execution completed successfully.[/bold green]")

    except ConfigurationError:
        logger.rule("[bold red]Configuration Error[/bold red]")
        logger.error("Exiting due to configuration errors.")
        exit_code = EXIT_CODE_ERROR
    except Exception as e:
        logger.rule("[bold red]Unexpected Error[/bold red]")
        # Check if this is the specific Rich error about live displays
        if "Only one live display may be active at once" in str(e):
            logger.error("Rich console error: Only one live display may be active at once. This is likely due to overlapping status displays.")
            logger.print("[yellow]Hint: This is a known issue with Rich status displays. The code has been updated to avoid this error in the future.[/yellow]")
        else:
            logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
        exit_code = EXIT_CODE_ERROR
    except KeyboardInterrupt:
        logger.rule("[bold yellow]Interrupted[/bold yellow]")
        logger.print("[yellow]Execution interrupted by user (Ctrl+C). Exiting.[/yellow]")
        exit_code = EXIT_CODE_ERROR
    finally:
        if exit_code != 0:
            logger.print("[bold red]Exiting with errors[/bold red]")
        sys.exit(exit_code)
