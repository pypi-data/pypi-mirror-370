import re
from typing import List, Tuple, Type

from langchain.tools import BaseTool
from langchain_community.agent_toolkits.base import BaseToolkit
from pydantic import BaseModel

# Import the Rich logger instead of configuring a basic logger
from codemie.logging import logger


class RemoteToolMetadata(BaseModel):
    name: str
    label: str = ''
    description: str = ''
    react_description: str = ''
    allowed_patterns: List[Tuple[str, str]] = []
    denied_patterns: List[Tuple[str, str]] = []

class RemoteInput(BaseModel):
    pass

class RemoteToolkit(BaseToolkit):
    pass

class RemoteTool(BaseTool):
    name: str = None
    description: str = None
    args_schema: Type[BaseModel] = None
    denied_patterns: List[Tuple[str, str]] = []
    allowed_patterns: List[Tuple[str, str]] = []

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "args_schema": self.args_schema().schema() if self.args_schema else None
        }

    def sanitize_input(cls,arg: str) -> ValueError|None:
        """
        Sanitize input arg to prevent potentially dangerous inputs.
        """

        for pattern, message in cls.denied_patterns:
            if re.search(pattern, arg):
                error = f"Potentially dangerous input detected: {message}"
                logger.error(error)
                return ValueError(error)
            
        for pattern, message in cls.allowed_patterns:
            if re.search(pattern, arg):
                return None
            else:
                error = f"Input not matched allowed patterns: {[message for pattern, message in cls.allowed_patterns]}"
                logger.error(error)
                return ValueError(error)

        return None
