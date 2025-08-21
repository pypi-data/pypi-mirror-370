from codemie.toolkit import RemoteToolkit
from tools import *

class Toolkit(RemoteToolkit):
    def get_tools(self):
        return [
            TimeTool(),
            CalculatorTool(),
            DockerTool()
        ]