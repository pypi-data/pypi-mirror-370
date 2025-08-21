from typing import Optional, Callable

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from codemie.logging import logger
import asyncio
import json
import uuid
from .util.term_util import format_tool_message


class RemoteTool(BaseModel):
    tool: BaseTool
    subject: str
    tool_result_converter: Optional[Callable[[ToolMessage], str]] = None

    def tool_schema(self):
        # Convert args_schema to JSON schema if it's a Pydantic model class
        args_schema_dict = None
        if self.tool.args_schema:
            if isinstance(self.tool.args_schema, dict):
                # It's already a dictionary, use it directly
                args_schema_dict = self.tool.args_schema
            elif hasattr(self.tool.args_schema, 'model_json_schema'):
                # Pydantic v2
                args_schema_dict = self.tool.args_schema.model_json_schema()
            else:
                # Fallback: try to get string representation
                args_schema_dict = str(self.tool.args_schema)
            
            # Ensure 'properties' field exists in args_schema_dict as required by GPT models
            if isinstance(args_schema_dict, dict) and 'properties' not in args_schema_dict:
                args_schema_dict['properties'] = {}

        return {
            "name": self.tool.name,
            "subject": self.subject,
            "description": self.tool.description,
            "args_schema": args_schema_dict
        }

    async def execute_tool_with_timeout(self, query, timeout):
        error_message = "Call to the tool timed out."
        try:
            tool_input = json.loads(query)
            tool_response = await asyncio.wait_for(
                self.tool.arun(tool_input, tool_call_id=str(uuid.uuid4())), timeout
            )
            logger.info(format_tool_message(self.tool.name, tool_input, tool_response))
            return tool_response

        except asyncio.TimeoutError:
            separator = "!" * 50
            error_msg = f"\n{separator}\nTool '{self.tool.name}' operation timed out after {timeout} seconds\n{separator}"
            logger.error(error_msg)
            return error_message
        except json.JSONDecodeError:
            separator = "!" * 50
            error_msg = f"\n{separator}\nTool '{self.tool.name}' failed to decode JSON input\n{separator}"
            logger.error(error_msg)
            return "Failed to decode JSON input."
        except Exception as e:
            separator = "!" * 50
            error_msg = f"\n{separator}\nTool '{self.tool.name}' error: {e}\n{separator}"
            logger.error(error_msg)
            return f"An error occurred: {e}"