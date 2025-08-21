import asyncio
from codemie.client import PluginClient
from toolkit import Toolkit


async def main():
    plugin = PluginClient(
        tools=Toolkit().get_tools())
    await plugin.connect()


asyncio.run(main())
