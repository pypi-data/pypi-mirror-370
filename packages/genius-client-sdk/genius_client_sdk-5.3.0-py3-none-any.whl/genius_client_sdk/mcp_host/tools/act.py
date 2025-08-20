from mcp import Tool
from typing import Union, Dict
from pydantic import BaseModel, ConfigDict, Field

from genius_client_sdk.mcp_host.tools.base import ToolBase
from genius_client_sdk.mcp_host.tools.runner import AgentRunner


class ActToolRequest(BaseModel):
    """
    Represents the data needed to run SDK Act method.
    """

    model_config = ConfigDict(title="Act Request")

    observation: Union[int, str, Dict[str, Union[int, str]]] = Field(
        title="Observation", description="The observation data"
    )
    policy_len: int = Field(
        default=2, title="Policy length", description="The length of the policy", lt=5
    )


# TODO: act response
class ActTool(ToolBase[ActToolRequest, dict]):
    """
    Represents the data needed to run SDK act tool.
    """

    def __init__(self, agent: AgentRunner):
        super().__init__(agent, ActToolRequest)

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="act",
            description="to perform action selection given a POMDP model structure and observation vector",
            inputSchema=ActToolRequest.model_json_schema(),
        )

    def handle_run_tool(self, args: ActToolRequest) -> dict:
        result = self.agent.act(
            observation=args.observation,
            policy_len=args.policy_len,
        )
        return result
