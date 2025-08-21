from codemie.toolkit import RemoteTool, logger, RemoteInput
from pydantic import Field
from typing import Type

from datetime import datetime
class TimeTool(RemoteTool):
    name: str = "_Time"
    description: str = "Tool to get the current. No arguments required"
    args_schema: Type[RemoteInput] = RemoteInput

    def _run(self, *args, **kwargs):
        logger.info(f"CodeMie tool {self.name} running with args: {args} and kwargs: {kwargs}")
        return str(datetime.now().isoformat())

class CalcInput(RemoteInput):
    a: float = Field(None, description="Input must be rounded to 2 decimal places.")
    b: float = Field(None, description="Input must be rounded to 2 decimal places.")
    action: str = Field(None, description="Action to perform on a and b. Valid actions are: +, -, *, /")

import operator
class CalculatorTool(RemoteTool):
    name: str = "_Calculator"
    description: str = "Tool to do math with two numbers."
    args_schema: Type[RemoteInput] = CalcInput

    def _run(self, a: int, b: int, action: str, *args, **kwargs):
        logger.info(f"CodeMie tool {self.name} running with args: {args} and kwargs: {kwargs}")
        actions = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
        }
        
        if action not in actions:
            raise ValueError(f"Invalid operator: {action}")
        
        result = actions[action](a, b)
        return str(result)

import subprocess
class DockerInput(RemoteInput):
    docker_args: list = Field(None, description="List of docker arguments to pass to docker CLI.")

class DockerTool(RemoteTool):
    name: str = "_Docker"
    description: str = "Docker Command Line Tool. All input is passed to docker CLI Command."
    args_schema: Type[RemoteInput] = DockerInput

    def _run(self, docker_args: list, *args, **kwargs):
        docker_command = "docker " + " ".join(docker_args)
        process = subprocess.Popen(docker_command, stdout=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        if process.returncode != 0:
            return str(error)
        else:
            return output.decode('utf-8')