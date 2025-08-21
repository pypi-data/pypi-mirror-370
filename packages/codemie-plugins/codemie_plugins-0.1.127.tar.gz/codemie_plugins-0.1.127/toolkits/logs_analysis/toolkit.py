from codemie.toolkit import RemoteToolkit
from toolkits.core.file_system_tools import ReadFileTool, ListDirectoryTool, WriteFileTool
from toolkits.logs_analysis.parse_logs_tool import ParseLogFileTool


class Toolkit(RemoteToolkit):
    def get_tools(self, root_dir: str = "."):
        return [
            ReadFileTool(root_dir=root_dir),
            ListDirectoryTool(root_dir=root_dir),
            WriteFileTool(root_dir=root_dir),
            ParseLogFileTool(root_dir=root_dir),
        ]
