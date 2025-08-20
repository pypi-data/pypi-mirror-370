from typing import Dict, Union
from mcp import Tool
from pydantic import BaseModel, ConfigDict, Field

from genius_client_sdk.mcp_host.tools.base import ToolBase
from genius_client_sdk.mcp_host.tools.runner import AgentRunner


class InferToolRequest(BaseModel):
    """
    Represents the data needed to run SDK Infer method.
    """

    model_config = ConfigDict(title="Infer Request")

    variables: Union[str, list] = Field(
        title="variables", description="A list of the variable(s) to infer."
    )
    evidence: Dict[str, Union[str, int, float]] = Field(
        title="evidence", description="A dictionary containing observed data."
    )


class InferToolResponse(BaseModel):
    """
    Represents the data needed to run SDK Infer method.
    """

    model_config = ConfigDict(title="Probabilities JSON Format")

    probabilities: Dict[
        str, Union[str, int, float, Dict[str, Union[str, int, float]]]
    ] = Field(
        title="probabilities",
        description="A dictionary containing probabilities of each variable.",
    )


class InferTool(ToolBase[InferToolRequest, InferToolResponse]):
    """
    Represents the data needed to run SDK Infer tool.
    """

    def __init__(self, agent: AgentRunner):
        super().__init__(agent, InferToolRequest)

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="infer",
            description="to perform inference given some evidence and a variable of interest",
            inputSchema=InferToolRequest.model_json_schema(),
        )

    def handle_run_tool(self, args: InferToolRequest) -> InferToolResponse:
        result = self.agent.infer(
            variables=args.variables,
            evidence=args.evidence,
        )

        probabilities = InferToolResponse.model_validate(result)  # type: ignore
        return probabilities  # Extra result
