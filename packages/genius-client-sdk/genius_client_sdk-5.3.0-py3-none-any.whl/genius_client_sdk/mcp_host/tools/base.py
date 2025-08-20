from typing import Any, Dict, Generic, TypeVar
from abc import ABC, abstractmethod

from mcp import Tool
from pydantic import BaseModel

from genius_client_sdk.mcp_host.tools.runner import AgentRunner
from genius_client_sdk.mcp_host.utils.validate import try_convert_str_value_to_json

TReq = TypeVar("TReq", bound=BaseModel)
TRes = TypeVar("TRes")


class ToolBase(ABC, Generic[TReq, TRes]):
    """ToolBase is the interface for integrating AgentRunner with MCP."""

    def __init__(self, agent: AgentRunner, typed_arg: type[TReq]):
        assert isinstance(agent, AgentRunner), (
            "agent must be an instance of AgentRunner"
        )

        self.agent = agent
        self.type_arg = typed_arg

    @abstractmethod
    def get_tool_definition(self) -> Tool:
        """Return the tool definition for MCP.
        Returns:
            Tool: The tool definition for MCP.
        """
        pass

    def run_tool(self, args: Dict[str, Any]) -> TRes:
        """Apply validation to the input arguments like Stringified JSON values and type checking based on Pydantic model.
        Args:
            args (Dict[str, Any]): The input arguments for the tool.
        Returns:
            TRes: The result of the tool execution.
        raises:
            ValueError: If the input arguments do not match the expected type.
            ValidationError: If the input arguments do not pass the Pydantic model validation.
        """
        # convert stringified JSON to dict
        removed_stringified_args = try_convert_str_value_to_json(args)

        typed_arg = self.type_arg.model_validate(removed_stringified_args)

        return self.handle_run_tool(typed_arg)

    @abstractmethod
    def handle_run_tool(self, args: TReq) -> TRes:
        """Handle the execution of the tool with the validated arguments.

        Args:
            args (TReq): The sanitized and validated input arguments for the tool.

        Returns:
            TRes: The result of the tool execution.
        """
        pass
