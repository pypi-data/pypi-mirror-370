import asyncio
from codemie.client import PluginClient
from toolkit import Toolkit

if __name__ == "__main__":
    plugin = PluginClient(
        tools=Toolkit().get_tools())
    asyncio.run(plugin.connect())