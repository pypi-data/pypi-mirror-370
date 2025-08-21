import asyncio
import json
import os
import re
import uuid
from typing import Dict, Optional, Callable

import certifi
import nats
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from rich.console import Console

import codemie.generated.proto.v1.service_pb2 as service_pb2
from codemie.logging import logger
from codemie.remote_tool import RemoteTool

console = Console()

class NatsClient:

    session_id: str = str(uuid.uuid4())
    nc: Optional[nats.NATS]
    nats_config: dict
    nats_max_payload: str
    label: str
    tools: Dict[str, RemoteTool] = {}
    plugin_key: str
    timeout: int
    live_update_interval: int = 60  # Send live updates every 60 seconds
    live_reply_timeout: int = 5     # seconds timeout for live reply

    _running: bool = False
    _connection_established: bool = False

    def __init__(self):
        self.plugin_key = os.getenv("PLUGIN_KEY")
        self.timeout = int(os.getenv("PLUGIN_TIMEOUT", "60"))
        self.live_update_interval = int(os.getenv("LIVE_UPDATE_INTERVAL", "60"))
        self.debug_updates = os.getenv("DEBUG_UPDATES", "false").lower() == "true"
        self.live_reply_timeout = int(os.getenv("LIVE_REPLY_TIMEOUT", "5"))
        self.tool_execution_timeout = int(os.getenv("TOOL_EXECUTION_TIMEOUT", "60"))
        nats_uri = os.getenv("PLUGIN_ENGINE_URI")
        nats_options = {
            "user": self.plugin_key,
            "password": self.plugin_key,
            "max_reconnect_attempts": -1,
            "connect_timeout": self.timeout,
            "drain_timeout": 1.0  # Set a short drain timeout to avoid hanging during shutdown
        }

        if nats_uri.startswith("tls://"):
            nats_options["tls_handshake_first"] = True

        self.nats_config = {
            "servers": [nats_uri],
            "options": nats_options
        }

        self.label = os.getenv("PLUGIN_LABEL") if os.getenv("PLUGIN_LABEL") else "default"
        self.nats_max_payload = os.environ.get("NATS_MAX_PAYLOAD", None)

        # Explicitly set the path to the trusted certificates (not used for plain connections)
        os.environ['SSL_CERT_FILE'] = os.getenv('SSL_CERT_FILE', os.path.relpath(certifi.where()))


    def add_tool(self, tool: BaseTool, tool_result_converter: Optional[Callable[[ToolMessage], str]] = None):
        if self._running:
            raise RuntimeError("Can't add new tools while running")
        self.tools[tool.name] = RemoteTool(
            tool=tool,
            subject=f"{self.plugin_key}.{self.session_id}.{self.label}.{tool.name}",
            tool_result_converter=tool_result_converter
        )

    async def connect(self):
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
            logger.print(f"\n{separator}\n[cyan]Setting NATS max payload to {self.nats_max_payload} bytes[/cyan]\n{separator}")
            self.nc._max_payload = int(self.nats_max_payload)

        await self._subscribe()

    async def run(self):
        self._running = True
        try:
            await self._send_live_updates()
        except RuntimeError as e:
            if "already running" in str(e):
                logger.warning("Event loop is already running.")
                raise RuntimeError("Event loop is already running.")
            raise

    async def disconnect(self):
        self._running = False

        # Try to publish disconnect notification, but don't let failures stop the shutdown
        try:
            if self.nc:
                await self._publish(f"{self.plugin_key}.disconnected", self.session_id.encode("utf-8"))
        except Exception as e:
            logger.error(f"Error publishing disconnect notification: {str(e)}")

        # Handle NATS client drain with special handling for cancellation
        try:
            if self.nc:
                logger.print("[cyan]Draining NATS connection[/cyan]")
                # Using a shorter timeout for drain to avoid long waits during cancellation
                drain_future = self.nc.drain()

                # Set a short timeout to avoid waiting too long during shutdown
                try:
                    await asyncio.wait_for(drain_future, timeout=1.0)
                    logger.print("[cyan]NATS connection drained[/cyan]")
                except asyncio.TimeoutError:
                    logger.print("[yellow]NATS drain timed out, continuing shutdown[/yellow]")
                except asyncio.CancelledError:
                    # This is expected during Ctrl+C handling, suppress the error
                    logger.print("[yellow]NATS drain was cancelled, continuing shutdown[/yellow]")
                
                self.nc = None
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def _publish(self, subject: str, payload: bytes, reply: Optional[str] = None):
        if not self.nc:
            raise RuntimeError("NATS client is not connected")

        try:
            if reply:
                await self.nc.publish(subject, payload, reply=reply)
            else:
                await self.nc.publish(subject, payload)
        except Exception as e:
            logger.error(f"Error publishing message to subject {subject}: {str(e)}")
            raise

    async def _send_live_updates(self):
        while self._running:
            try:
                await self._send_live_update()
                # Wait for 60 seconds before sending the next update
                await asyncio.sleep(self.live_update_interval)
            except asyncio.CancelledError:
                logger.info("Live updates were cancelled")
                break

    async def _send_live_update(self):
        reply = f"{self.plugin_key}.live.reply"
        await self._publish(f"{self.plugin_key}.live", self.session_id.encode("utf-8"), reply=reply)

        # Reset connection status before waiting for reply
        self._connection_established = False

        # Wait for the live reply timeout
        await asyncio.sleep(self.live_reply_timeout)

        # Check if connection was established (will be set to True in _handle_live_response)
        if not self._connection_established:
            logger.warning(f"[yellow]Live connection reply timed out after {self.live_reply_timeout} seconds. "
                           f"Verify your connectivity just using 'show tools' or invoking any other tool by assistant."
                           f"[/yellow]")

    async def _on_error(self, e):
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"NATS error: {str(e)}\n{error_trace}")

    async def _on_disconnect(self):
        logger.warning("NATS disconnected")

    async def _on_reconnect(self):
        logger.print("[cyan]NATS reconnected[/cyan]")

    async def _on_drained(self):
        logger.print("[cyan]NATS connection drained[/cyan]")

    async def _on_close(self):
        logger.print("[cyan]NATS connection closed[/cyan]")
        self._running = False

    async def _subscribe(self):
        if not self.nc:
            raise RuntimeError("NATS client is not connected")

        await self.nc.subscribe(
            f"{self.plugin_key}.list",
            cb=self._handle_list_request
        )

        await self.nc.subscribe(
            f"{self.plugin_key}.live.reply",
            cb=self._handle_live_response
        )

        await self.nc.subscribe(
            f"{self.plugin_key}.{self.session_id}.{self.label}.*",
            cb=self._handle_tool_request
        )

        logger.print(f"[cyan]Subscribed to NATS subjects, ready to serve {len(self.tools)} tools[/cyan]")

    async def _handle_list_request(self, msg):
        logger.print(f"[cyan]Remote server asked list of available tools, found {len(self.tools)}[/cyan]")
        await self.nc.publish(msg.reply, json.dumps(
            list(map(lambda tool: tool.tool_schema(), self.tools.values()))
        ).encode("utf-8"))

    async def _handle_live_response(self, msg):
        # Mark connection as established when we receive a reply
        self._connection_established = True
        response = msg.data.decode()
        if response == "no tools found":
            logger.print("[yellow]No tools has been connected to server by some reason. "
                         "Try reconnect later or contact CodeMie team support 'https://epa.ms/codemie-support'[/yellow]")
        elif ("alive" in response) and self.debug_updates:
            logger.print(f"[green]Live updates | Successful readiness check: {response} [/green]")
        else:
            logger.print(f"[green]Live updates | Connection response from server: {msg.data.decode()}[/green]")

    async def _handle_tool_request(self, msg):
        pattern = '([^.]*)\\.([^.]*)\\.([^.]*)\\.([^.]*)'
        match = re.search(pattern, msg.subject, re.IGNORECASE)
        if not match:
            raise RuntimeError("Invalid subject " + msg.subject)

        plugin_key = match.group(1)
        session_id = match.group(2)
        label = match.group(3)
        tool_name = match.group(4)

        logger.print(f"[cyan]Tool request for {tool_name}[/cyan]")
        if session_id != self.session_id:
            raise RuntimeError("Invalid session_id")

        if label != self.label:
            raise RuntimeError("Invalid label")

        if plugin_key != self.plugin_key:
            raise RuntimeError("Invalid plugin_key")

        if tool_name not in self.tools:
            raise RuntimeError("Invalid tool requested " + tool_name)

        tool: RemoteTool = self.tools[tool_name]

        request = service_pb2.ServiceRequest()
        request.ParseFromString(msg.data)
        if not request.IsInitialized() or request.meta.handler != service_pb2.Handler.RUN:
            raise RuntimeError("Invalid request")

        query = request.puppet_request.lc_tool.query
        response = service_pb2.ServiceResponse()
        response.meta.subject = msg.subject
        response.meta.handler = service_pb2.Handler.RUN
        response.meta.puppet = service_pb2.Puppet.LANGCHAIN_TOOL

        try:
            tool_response = await tool.execute_tool_with_timeout(query, self.tool_execution_timeout)
            converted_response = (
                tool.tool_result_converter(tool_response) if tool.tool_result_converter else str(tool_response)
            )
            response.puppet_response.lc_tool.result = converted_response
        except Exception as exc:
            separator = "!" * 50
            error_message = f"Tool '{tool_name}' got error: {exc}"
            logger.error(f"\n{separator}\n{error_message}\n{separator}", exc_info=True)
            response.puppet_response.lc_tool.error = error_message

        await self.nc.publish(msg.reply, response.SerializeToString())
    
    