import asyncio
import os

from codemie.client import PluginClient
from codemie.toolkit import logger
from toolkits.development.toolkit import FileSystemAndCommandToolkit

root_dir: str = os.getenv("REPO_FILE_PATH")


async def main():
    if not os.getenv("PLUGIN_KEY"):
        logger.error("Environment variable PLUGIN_KEY is not defined.")
    if not root_dir:
        logger.error("Environment variable REPO_FILE_PATH is not defined.")
        exit(1)
    else:
        logger.info(f"Run Development Plugin. REPO_FILE_PATH={root_dir}")
        plugin_label = os.path.basename(root_dir)
        os.environ["PLUGIN_LABEL"] = plugin_label
        timeout = os.getenv('COMMAND_LINE_TOOL_TIMEOUT', 300)
        plugin = PluginClient(tools=FileSystemAndCommandToolkit().get_tools(root_dir), timeout=timeout)
        await plugin.connect()

asyncio.run(main())
