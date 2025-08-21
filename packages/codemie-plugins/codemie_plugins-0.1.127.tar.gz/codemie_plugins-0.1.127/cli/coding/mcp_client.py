"""
MCP client functionality for the coding agent.
This module handles all MCP-related operations, including server configuration,
tool creation, and client management.
"""

import json
import os
from typing import Any, Dict, List, Optional

from langchain_core.tools import BaseTool
from rich.console import Console

from toolkits.mcp.main import ArgumentHandler

console = Console()


class MCPClientManager:
    """Manages MCP client connections and tool creation."""

    def __init__(self, mcp_servers: Optional[str] = None, disable_default_tools: bool = False):
        """Initialize the MCP client manager.
        
        Args:
            mcp_servers: Comma-separated list of MCP server names
            disable_default_tools: Whether default tools should be disabled
        """
        self.mcp_servers = mcp_servers
        self.disable_default_tools = disable_default_tools
        
    def setup_mcp_tools(self) -> List[BaseTool]:
        """Set up MCP tools based on the specified servers.
        
        Returns:
            List of tools created from MCP servers
        """
        if not self.mcp_servers:
            return []

        try:
            # Parse server names
            server_names = ArgumentHandler.parse_server_names(self.mcp_servers)
            if not server_names:
                console.print("[yellow]No valid MCP server names provided. Skipping MCP integration.[/yellow]")
                return []

            console.print(f"[cyan]Initializing MCP servers: {', '.join(server_names)}[/cyan]")

            # Get filtered server configurations based on requested names
            filtered_servers = self._get_filtered_servers(server_names)
            if not filtered_servers:
                return []

            # Get the tools using our event loop
            tools = self._create_mcp_sync_tools(filtered_servers)

            if tools:
                console.print(f"[green]Successfully loaded {len(tools)} tools from MCP servers[/green]")

            return tools

        except Exception as e:
            console.print(f"[bold red]Error setting up MCP tools:[/bold red] {str(e)}")
            return []

    def _get_filtered_servers(self, server_names: List[str]) -> Dict[str, Any]:
        """Get filtered server configurations based on requested names.
        
        Args:
            server_names: List of server names to filter
            
        Returns:
            Dictionary of server configurations
        """
        # Get MCP servers from global config
        all_servers = self._get_global_mcp_servers()

        # Validate that all requested servers exist
        missing_servers = [s for s in server_names if s not in all_servers]
        if missing_servers:
            console.print(f"[bold red]Error:[/bold red] The following MCP servers were not found in global config: {', '.join(missing_servers)}")
            console.print("[yellow]Use 'codemie-plugins mcp list' to see available servers or add them to global config[/yellow]")
            return {}

        # Skip filesystem and cli servers unless default tools are disabled
        if not self.disable_default_tools and any(s in server_names for s in ["filesystem", "cli"]):
            console.print("[yellow]Filesystem and CLI tools are enabled by default. Skipping these MCP servers.[/yellow]")
            # Remove these from the list
            server_names = [s for s in server_names if s not in ["filesystem", "cli"]]
            if not server_names:
                return {}
        elif self.disable_default_tools and any(s in server_names for s in ["filesystem", "cli"]):
            console.print("[green]Default tools disabled. Loading filesystem and CLI tools from MCP servers.[/green]")

        # Create filtered server config with only the requested servers
        return {name: all_servers[name] for name in server_names}

    def _get_global_mcp_servers(self) -> Dict[str, Any]:
        """Get MCP servers from the global config.json only.
        
        Returns:
            Dictionary of server configurations
        """
        # Load global servers
        global_config_path = os.path.expanduser('~/.codemie/config.json')

        if not os.path.exists(global_config_path):
            console.print(f"[yellow]Warning:[/yellow] Global config file not found at {global_config_path}")
            return {}

        try:
            with open(global_config_path, 'r') as f:
                global_config = json.load(f)
                global_servers = global_config.get("mcpServers", {})

            if not global_servers:
                console.print(f"[yellow]Warning:[/yellow] No MCP servers defined in global config at {global_config_path}")

            return global_servers
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Error reading global configuration: {str(e)}")
            return {}

    def _create_mcp_sync_tools(self, servers: Dict[str, Any]) -> List[BaseTool]:
        """Create tools that handle their own async/sync conversion.
        
        Args:
            servers: Dictionary of server configurations
            
        Returns:
            List of tools created from MCP servers
        """

        try:
            # Get the initial async tools
            async_tools = self._fetch_async_tools(servers)
            
            # Convert async tools to sync tools
            converted_tools = self._convert_async_to_sync_tools(async_tools, servers)

            if converted_tools:
                console.print(f"[green]Successfully created {len(converted_tools)} tools with independent execution contexts[/green]")

            return converted_tools

        except Exception as e:
            console.print(f"[bold red]Error creating MCP tools:[/bold red] {str(e)}")
            return []
            
    def _fetch_async_tools(self, servers: Dict[str, Any]) -> List[Any]:
        """Fetch async tools from MCP servers.
        
        Args:
            servers: Dictionary of server configurations
            
        Returns:
            List of async tools
        """
        import asyncio

        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Create a temporary loop for initialization
        init_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(init_loop)
        
        try:
            # Define async function to get tools through context manager
            async def get_initial_tools():
                async with MultiServerMCPClient(servers) as client:
                    return client.get_tools()

            # Get the initial tools
            return init_loop.run_until_complete(get_initial_tools())
        finally:
            init_loop.close()
            
    def _convert_async_to_sync_tools(self, async_tools: List[Any], server_config: Dict[str, Any]) -> List[BaseTool]:
        """Convert async tools to sync tools.
        
        Args:
            async_tools: List of async tools
            server_config: Dictionary of server configurations
            
        Returns:
            List of sync tools
        """
        from langchain_core.tools import StructuredTool
        
        converted_tools = []
        
        for async_tool in async_tools:
            # Extract tool metadata
            tool_metadata = self._extract_tool_metadata(async_tool)
            
            # Create sync function wrapper
            sync_fn = self._create_sync_function(tool_metadata["name"], server_config)
            
            # Set function metadata
            sync_fn.__name__ = tool_metadata["name"]
            sync_fn.__doc__ = tool_metadata["description"]
            
            # Create structured tool
            converted_tool = StructuredTool.from_function(
                func=sync_fn,
                name=tool_metadata["name"],
                description=tool_metadata["description"],
                args_schema=tool_metadata["args_schema"],
                return_direct=tool_metadata["return_direct"],
                handle_tool_error=True
            )
            
            converted_tools.append(converted_tool)
            
        return converted_tools
        
    def _extract_tool_metadata(self, async_tool: Any) -> Dict[str, Any]:
        """Extract metadata from an async tool.
        
        Args:
            async_tool: Async tool
            
        Returns:
            Dictionary of tool metadata
        """
        return {
            "name": async_tool.name,
            "description": async_tool.description,
            "args_schema": async_tool.args_schema,
            "return_direct": async_tool.return_direct
        }
        
    def _create_sync_function(self, tool_name: str, server_config: Dict[str, Any]):
        """Create a synchronous function wrapper for an async tool.
        
        Args:
            tool_name: Name of the tool
            server_config: Server configuration
            
        Returns:
            Synchronous function that wraps the async tool
        """
        import asyncio

        
        def sync_function(**kwargs):
            # Create a fresh event loop for this invocation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                return loop.run_until_complete(self._execute_async_tool(tool_name, server_config, kwargs))
            except Exception as e:
                return f"Error executing {tool_name}: {str(e)}"
            finally:
                loop.close()
                
        return sync_function
        
    async def _execute_async_tool(self, tool_name: str, server_config: Dict[str, Any], kwargs: Dict[str, Any]) -> Any:
        """Execute an async tool.
        
        Args:
            tool_name: Name of the tool
            server_config: Server configuration
            kwargs: Tool arguments
            
        Returns:
            Tool execution result
        """
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        async with MultiServerMCPClient(server_config) as client:
            tools = client.get_tools()
            # Find the right tool by name
            for tool in tools:
                if tool.name == tool_name:
                    # Execute it with the provided arguments
                    return await tool.ainvoke(kwargs)
            # If we get here, we couldn't find the tool
            return f"Error: Could not find tool '{tool_name}'"