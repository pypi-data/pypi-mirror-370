import json
from typing import Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel

from genius_client_sdk.mcp_host.tools.act import ActTool
from genius_client_sdk.mcp_host.tools.infer import InferTool
from genius_client_sdk.mcp_host.tools.runner import AgentRunner


def create_mcp_agent_server(agent: AgentRunner) -> Server:
    """
    Factory function to create host MCP server.

    Args:
        agent (AgentRunner): The agent instance to be used.

    Returns:
        Server: The MCP server instance().
    """

    assert isinstance(agent, AgentRunner), "agent must be an instance of AgentRunner"

    # Tools pre-defined
    infer_tool = InferTool(agent)
    act_tool = ActTool(agent)

    # Generic and static definitions
    infer_tool_definition = infer_tool.get_tool_definition()
    act_tool_definition = act_tool.get_tool_definition()

    mcpServer: Server = Server(
        name="mcp-agent",
        version="0.1.0",
    )

    @mcpServer.list_tools()
    async def list_tools() -> list[Tool]:
        """List available agent tools."""

        return [infer_tool_definition, act_tool_definition]

    @mcpServer.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls for inference and action decision."""
        try:
            response: dict | BaseModel
            match name:
                case "infer":
                    response = infer_tool.run_tool(arguments)
                case "act":
                    response = act_tool.run_tool(arguments)
                case _:
                    raise ValueError(f"Unknown tool: {name}")

            text_response = (
                response.model_dump_json(indent=2)
                if isinstance(response, BaseModel)
                else json.dumps(response, indent=2)
            )
            return [
                TextContent(
                    type="text",
                    text=text_response,
                )
            ]

        except Exception as e:
            raise ValueError(f"Error calling `{name}`: {str(e)}")

    return mcpServer
