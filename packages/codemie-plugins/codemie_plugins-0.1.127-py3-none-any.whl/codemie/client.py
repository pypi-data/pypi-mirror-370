"""Plugin client module."""
import random
import os
import asyncio
from typing import Optional, Callable

import certifi
from langchain_core.messages import ToolMessage
from pydantic import BaseModel
from langchain.tools import BaseTool

from codemie.nats_client import NatsClient
from codemie.toolkit import logger
from codemie.langchain.services import ToolService

class PluginClient:
    """Plugin client class."""
    def __init__(
            self,
            tools: list[BaseTool],
            tool_result_converter: Optional[Callable[[ToolMessage], str]] = None,
            timeout: int = int(os.getenv("PLUGIN_TIMEOUT", "60"))
    ):
        """Initialize PluginClient class."""
        if not os.getenv("PLUGIN_KEY"):
            logger.error("Plugin key is required.")
            raise SystemExit
        # Store passed parameters
        self.timeout = timeout
        self.tools = tools
        self.tool_result_converter = tool_result_converter

        # Store environment variables
        self.plugin_key = os.getenv("PLUGIN_KEY")
        self.plugin_id = str(random.randint(100000, 999999))
        self.plugin_label = os.getenv("PLUGIN_LABEL") if os.getenv("PLUGIN_LABEL") else "default"
        # Use LEGACY_PROTOCOL=true to enable the old approach
        self.legacy_protocol = os.getenv("LEGACY_PROTOCOL") == "true"

        if not os.getenv("PLUGIN_ENGINE_URI"):
            logger.error("Plugin engine URI is required.")
            raise SystemExit
        self.pe_uri = os.getenv("PLUGIN_ENGINE_URI")

        if not tools:
            logger.error("No tools provided.")
            raise SystemExit

        # Enrich tool details with plugin information
        self._enrich_tools_details()

        # Configure NATS options
        self.options = {
            "user": self.plugin_key,
            "password": self.plugin_key,
            "max_reconnect_attempts": -1,
            "connect_timeout": self.timeout
        }

        if self.pe_uri.startswith("tls://"):
            self.options["tls_handshake_first"] = True

        self.nats_config = {
            "servers": [self.pe_uri],
            "options": self.options
        }

        # Explicitly set the path to the trusted certificates (not used for plain connections)
        os.environ['SSL_CERT_FILE'] = os.getenv('SSL_CERT_FILE', os.path.relpath(certifi.where()))

        # Store tool services for management
        self.tool_services = []

    def _enrich_tools_details(self):
        """Enrich tools description with plugin information."""
        for tool in self.tools:
            if not tool.name.startswith("_"):
                tool.name = f"_{tool.name}"
            if isinstance(tool.args_schema, dict) and not tool.args_schema.get("title"):
                tool.args_schema["title"] = f"{tool.name}Args"
            if isinstance(tool.args_schema, BaseModel) and not tool.args_schema.title:
                tool.args_schema.title = f"{tool.name}Args"
            tool.description = f"""{tool.description}
            Plugin label: {self.plugin_label}
            Plugin ID: {self.plugin_id}
            """

    async def connect(self):
        # Show connection information
        logger.print(f"[cyan]Connecting to Plugin Engine: {self.pe_uri}. Timeout: {self.timeout}s[/cyan]")

        try:
            # Run the async connect in the event loop
            if self.legacy_protocol:
                await self.async_connect()
            else:
                await self.async_connect_experimental()
        except KeyboardInterrupt:
            logger.print("[cyan]Received keyboard interrupt, shutting down...[/cyan]")
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            raise

    async def async_connect_experimental(self):
        self.nc = NatsClient()
        for tool in self.tools:
            self.nc.add_tool(
                tool=tool,
                tool_result_converter=self.tool_result_converter
            )

        await self.nc.connect()
        try:
            await self.nc.run()
        except KeyboardInterrupt:
            logger.info("Shutting down due to keyboard interrupt")
            raise
        except Exception as e:
            logger.error(f"Error in tools: {str(e)}")
        finally:
            # Ensure all services are properly stopped
            await self.nc.disconnect()


    async def async_connect(self):
        """Asynchronously connect all tools to the plugin engine."""
        logger.print(f"[cyan]Starting Plugin ID: {self.plugin_id}, Label: {self.plugin_label}. Tools: {len(self.tools)}[/cyan]")

        # Create a ToolService for each tool
        self.tool_services = []
        for tool in self.tools:
            prefix = f"{self.plugin_key}.{self.plugin_id}.{self.plugin_label}"
            ts = ToolService(
                nats_config=self.nats_config,
                tool=tool,
                prefix=prefix,
                timeout=self.timeout,
                tool_result_converter=self.tool_result_converter,
            )
            self.tool_services.append(ts)

        # Start all services with a small delay between them
        tasks = []
        for ts in self.tool_services:
            task = await ts.start()
            tasks.append(task)
            await asyncio.sleep(3)  # Small delay between starting each service

        logger.print(f"[cyan]Started {len(tasks)} tool services[/cyan]")

        # Wait for all tasks to complete (they should run forever unless there's an error)
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.print("[cyan]Services are being cancelled[/cyan]")
        except Exception as e:
            logger.error(f"Error in tools: {str(e)}")
        finally:
            # Ensure all services are properly stopped
            await self.shutdown()

    async def shutdown(self):
        """Gracefully shutdown all services."""
        logger.print("[cyan]Shutting down all tool services[/cyan]")
        shutdown_tasks = []
        for ts in self.tool_services:
            shutdown_tasks.append(ts.stop())

        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks)
        logger.print("[cyan]All tool services shut down[/cyan]")
