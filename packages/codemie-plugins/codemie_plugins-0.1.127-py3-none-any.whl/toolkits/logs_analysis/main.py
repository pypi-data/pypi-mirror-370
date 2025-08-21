import asyncio
import os

from codemie.client import PluginClient
from codemie.toolkit import logger
from toolkits.logs_analysis.toolkit import Toolkit

root_dir: str = os.getenv("ROOT_DIR")


async def main():
    if not os.getenv("PLUGIN_KEY"):
        logger.error("Environment variable PLUGIN_KEY is not defined.")
    if not root_dir:
        logger.error("Environment variable ROOT_DIR is not defined.")
        exit(1)
    else:
        logger.info(f"Run Logs Analysis Plugin. ROOT_DIR={root_dir}")
        plugin_label = os.path.basename(root_dir)
        os.environ["PLUGIN_LABEL"] = plugin_label
        plugin = PluginClient(tools=Toolkit().get_tools(root_dir))
        await plugin.connect()

asyncio.run(main())

