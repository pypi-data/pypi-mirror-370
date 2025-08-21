import logging
import traceback
from abc import abstractmethod
from typing import Any, Optional

import tiktoken
from langchain_core.tools import BaseTool

from cli.coding.utils import sanitize_string

logger = logging.getLogger(__name__)


class CodeMieTool(BaseTool):
    base_name: Optional[str] = None
    handle_tool_error: bool = True
    tokens_size_limit: int = 10000
    throw_truncated_error: bool = False
    truncate_message: str = "Tool output is truncated, make more lightweight query."
    base_llm_model_name: str = "gpt-35-turbo"

    def _run(self, *args, **kwargs):
        try:
            result = self.execute(*args, **kwargs)
            output, _ = self._limit_output_content(result)
            return output
        except Exception:
            stacktrace = sanitize_string(traceback.format_exc())
            error_message = (f"Error calling tool: {self.name} with: \n"
                             f"Arguments: {kwargs}. \n"
                             f"The root cause is: '{stacktrace}'")
            return error_message

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass

    def calculate_tokens_count(self, output: Any) -> int:
        encoding = tiktoken.encoding_for_model(self.base_llm_model_name)
        tokens = encoding.encode(str(output))
        return len(tokens)

    def _limit_output_content(self, output: Any) -> Any:
        """
        Limit the size of the output based on token constraints.

        Args:
            output (Any): The content to be processed and potentially truncated.

        Returns:
            Tuple[Any, int]: The (possibly truncated) output and the token count.

        Raises:
            TruncatedOutputError: If the output exceeds the token size limit and throwing errors is enabled.
        """
        encoding = tiktoken.encoding_for_model(self.base_llm_model_name)
        tokens = encoding.encode(str(output))
        token_count = len(tokens)

        if token_count <= self.tokens_size_limit:
            return output, token_count

        # Output exceeds token limit: calculate truncation details
        truncate_ratio = self.tokens_size_limit / token_count
        truncated_data = encoding.decode(tokens[:self.tokens_size_limit])
        truncated_output = (
            f"{self.truncate_message} "
            f"Ratio limit/used_tokens: {truncate_ratio}. Tool output: {truncated_data}"
        )
        error_message = (
            f"{self.name} output is too long: {token_count} tokens. "
            f"Ratio limit/used_tokens: {truncate_ratio} for output tokens {self.tokens_size_limit}"
        )

        logger.error(error_message)

        if self.throw_truncated_error:
            raise ValueError(truncated_output)

        return truncated_output, token_count
