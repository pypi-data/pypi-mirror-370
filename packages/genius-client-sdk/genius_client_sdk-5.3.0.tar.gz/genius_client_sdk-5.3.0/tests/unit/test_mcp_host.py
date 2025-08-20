import json
import os
import pytest
from unittest.mock import patch

import mcp.types as types

from genius_client_sdk.agent import GeniusAgent
from genius_client_sdk.auth import ApiKeyConfig
from genius_client_sdk.mcp_host._mcp_adapter import GeniusMCPAgentAdapter
from genius_client_sdk.mcp_host._mcp_server import create_mcp_agent_server
from genius_client_sdk.mcp_host._mcp_env import get_config_from_env
from genius_client_sdk.mcp_host.utils.validate import try_convert_str_value_to_json


## Helper assertions
def assert_result_call(result: types.ServerResult) -> types.TextContent:
    """
    Helper function to assert the result of an inference call.
    Args:
        result (types.TextContent): The result of the call tool.
    """
    assert isinstance(result, types.ServerResult), (
        "Expected result to be a ServerResult"
    )
    assert isinstance(result.root, types.CallToolResult), (
        "Expected root to be a CallToolResult"
    )

    assert isinstance(result.root.content, list), "Expected 'content' to be a list"
    content, *extra_content = result.root.content
    assert len(extra_content) == 0, "Expected 'content' list to have one item"
    assert isinstance(content, types.TextContent), (
        "Expected first item in 'content' to be a TextContent"
    )

    return content


def test_agent_server_initialization():
    expected_protocol = "http"
    expected_hostname = "10.0.0.1"
    expected_port = "3003"
    expected_auth = "test_api_key"

    os.environ["SDK_AGENT_HTTP_PROTOCOL"] = expected_protocol
    os.environ["SDK_AGENT_HOSTNAME"] = expected_hostname
    os.environ["SDK_AGENT_PORT"] = expected_port
    os.environ["SDK_AGENT_API_KEY"] = expected_auth

    (cur_protocol, cur_hostname, cur_port, cur_auth) = get_config_from_env()

    assert cur_protocol == expected_protocol, (
        f"Expected protocol: {expected_protocol}, but got: {cur_protocol}"
    )
    assert cur_hostname == expected_hostname, (
        f"Expected hostname: {expected_hostname}, but got: {cur_hostname}"
    )
    assert cur_port == int(expected_port), (
        f"Expected port: {expected_port}, but got: {cur_port}"
    )

    assert isinstance(cur_auth, ApiKeyConfig), (
        f"Expected auth to be of type ApiKeyConfig, but got: {type(cur_auth)}"
    )
    assert cur_auth.api_key == expected_auth, (
        f"Expected auth api_key: {expected_auth}, but got: {cur_auth.api_key}"
    )


def test_agent_server_initialization_missing_proto():
    del os.environ["SDK_AGENT_HTTP_PROTOCOL"]
    os.environ["SDK_AGENT_HOSTNAME"] = "10.0.0.1"
    os.environ["SDK_AGENT_PORT"] = "3003"
    os.environ["SDK_AGENT_API_KEY"] = "test_api_key"
    with pytest.raises(SystemExit) as e:
        (cur_protocol, cur_hostname, cur_port, cur_auth) = get_config_from_env()

    assert e.type is SystemExit
    assert e.value.code == 1, f"Expected exit code 1, but got: {e.value.code}"


def test_agent_server_initialization_missing_host():
    os.environ["SDK_AGENT_HTTP_PROTOCOL"] = "http"
    del os.environ["SDK_AGENT_HOSTNAME"]
    os.environ["SDK_AGENT_PORT"] = "3003"
    os.environ["SDK_AGENT_API_KEY"] = "test_api_key"
    with pytest.raises(SystemExit) as e:
        (cur_protocol, cur_hostname, cur_port, cur_auth) = get_config_from_env()

    assert e.type is SystemExit
    assert e.value.code == 1, f"Expected exit code 1, but got: {e.value.code}"


def test_agent_server_initialization_missing_port():
    os.environ["SDK_AGENT_HTTP_PROTOCOL"] = "http"
    os.environ["SDK_AGENT_HOSTNAME"] = "10.0.0.1"
    del os.environ["SDK_AGENT_PORT"]
    os.environ["SDK_AGENT_API_KEY"] = "test_api_key"
    with pytest.raises(SystemExit) as e:
        (cur_protocol, cur_hostname, cur_port, cur_auth) = get_config_from_env()

    assert e.type is SystemExit
    assert e.value.code == 1, f"Expected exit code 1, but got: {e.value.code}"


def test_agent_server_initialization_invalid_port():
    os.environ["SDK_AGENT_HTTP_PROTOCOL"] = "http"
    os.environ["SDK_AGENT_HOSTNAME"] = "10.0.0.1"
    os.environ["SDK_AGENT_PORT"] = "a"
    os.environ["SDK_AGENT_API_KEY"] = "test_api_key"
    with pytest.raises(SystemExit) as e:
        (cur_protocol, cur_hostname, cur_port, cur_auth) = get_config_from_env()

    assert e.type is SystemExit
    assert e.value.code == 1, f"Expected exit code 1, but got: {e.value.code}"


def test_agent_server_initialization_invalid_port_range():
    os.environ["SDK_AGENT_HTTP_PROTOCOL"] = "http"
    os.environ["SDK_AGENT_HOSTNAME"] = "10.0.0.1"
    os.environ["SDK_AGENT_PORT"] = "321000"
    os.environ["SDK_AGENT_API_KEY"] = "test_api_key"
    with pytest.raises(SystemExit) as e:
        (cur_protocol, cur_hostname, cur_port, cur_auth) = get_config_from_env()

    assert e.type is SystemExit
    assert e.value.code == 1, f"Expected exit code 1, but got: {e.value.code}"


def test_agent_server_initialization_missing_api_key():
    os.environ["SDK_AGENT_HTTP_PROTOCOL"] = "http"
    os.environ["SDK_AGENT_HOSTNAME"] = "10.0.0.1"
    os.environ["SDK_AGENT_PORT"] = "3003"
    del os.environ["SDK_AGENT_API_KEY"]

    with pytest.raises(SystemExit) as e:
        (cur_protocol, cur_hostname, cur_port, cur_auth) = get_config_from_env()

    assert e.type is SystemExit
    assert e.value.code == 2, f"Expected exit code 1, but got: {e.value.code}"


def test_call_tool_args_using_invalid_input():
    content = '{"arg1": "value1","arg2": ["value1","value2"],"arg3": {"key1","key2":"value2"}}'

    with pytest.raises(ValueError) as e:
        try_convert_str_value_to_json(content)

    assert str(e).find("must be a dictionary") >= 0, (
        f"Expected error message to be in the exception: {e.value}"
    )


def test_call_tool_args_using_invalid_value():
    content = {
        "arg1": "value1",
        "arg2": '["value1","value2"]',
        "arg3": '{"key1","key2":"value2"}',
    }

    typed_content = try_convert_str_value_to_json(content)

    expected_content = {
        "arg1": "value1",
        "arg2": ["value1", "value2"],
        "arg3": content["arg3"],
    }

    assert typed_content == expected_content, (
        f"Expected content: {expected_content}, but got: {typed_content}"
    )


def test_call_tool_args_using_stringify_value():
    content = {
        "arg1": "value1",
        "arg2": '["value1","value2"]',
        "arg3": '{"key1":"value1","key2":"value2"}',
    }

    typed_content = try_convert_str_value_to_json(content)

    expected_content = {
        "arg1": "value1",
        "arg2": ["value1", "value2"],
        "arg3": {"key1": "value1", "key2": "value2"},
    }

    assert typed_content == expected_content, (
        f"Expected content: {expected_content}, but got: {typed_content}"
    )


def test_create_agent_server_invalid_dependency():
    agent = GeniusAgent()

    with pytest.raises(AssertionError) as e:
        create_mcp_agent_server(agent)

    assert str(e).find("agent must be an instance of AgentRunner") >= 0, (
        f"Expected error message to be in the exception: {e.value}"
    )


@pytest.mark.asyncio
async def test_list_tools():
    agent = GeniusAgent()

    with patch.object(agent, "get_model_from_server", return_value=None):
        agent_server = create_mcp_agent_server(GeniusMCPAgentAdapter(agent))

        handler = agent_server.request_handlers[types.ListToolsRequest]
        result = await handler(types.ListToolsRequest(method="tools/list"))

        assert isinstance(result, types.ServerResult), (
            "Expected result to be a ServerResult"
        )
        assert isinstance(result.root, types.ListToolsResult), (
            "Expected root to be a ListToolsResult"
        )

        tools = result.root.tools
        assert isinstance(tools, list), "Expected 'tools' to be a list"
        assert len(tools) == 2, "Expected 'tools' list to have 2 items"


@pytest.mark.asyncio
async def test_call_infer_tool():
    response_mock = {"probabilities": {"no": 0.1, "yes": 0.9}}
    agent = GeniusAgent()

    with (
        patch.object(agent, "get_model_from_server", return_value=None),
        patch.object(agent, "infer", return_value=response_mock),
    ):
        agent_server = create_mcp_agent_server(GeniusMCPAgentAdapter(agent))

        handler = agent_server.request_handlers[types.CallToolRequest]
        result = await handler(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="infer",
                    arguments={
                        "variables": ["wet_grass"],
                        "evidence": {"rain": "yes", "sprinkler": "off"},
                    },
                ),
            )
        )

        content = assert_result_call(result)
        # Deserialize the content to assert the response
        jsonResult = json.loads(content.text)
        assert jsonResult == response_mock, (
            f"Expected: {response_mock} to match the received: {result}"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "evidence_payload", ['{"rain": "yes", "sprinkler": "off"}', "{}"]
)
async def test_call_infer_tool_stringified_evidence_arg(evidence_payload):
    response_mock = {"probabilities": {"no": 0.1, "yes": 0.9}}
    agent = GeniusAgent()

    with (
        patch.object(agent, "get_model_from_server", return_value=None),
        patch.object(agent, "infer", return_value=response_mock),
    ):
        agent_server = create_mcp_agent_server(GeniusMCPAgentAdapter(agent))

        handler = agent_server.request_handlers[types.CallToolRequest]
        result = await handler(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="infer",
                    arguments={
                        "variables": "wet_grass",
                        # Ollama stringified JSON
                        "evidence": evidence_payload,
                    },
                ),
            )
        )

        content = assert_result_call(result)
        # Deserialize the content to assert the response
        jsonResult = json.loads(content.text)
        assert jsonResult == response_mock, (
            f"Expected: {response_mock} to match the received: {result}"
        )


@pytest.mark.asyncio
async def test_call_infer_tool_stringified_variables_arg():
    response_mock = {"probabilities": {"no": 0.11, "yes": 0.89}}
    agent = GeniusAgent()

    with (
        patch.object(agent, "get_model_from_server", return_value=None),
        patch.object(agent, "infer", return_value=response_mock),
    ):
        agent_server = create_mcp_agent_server(GeniusMCPAgentAdapter(agent))

        handler = agent_server.request_handlers[types.CallToolRequest]
        result = await handler(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="infer",
                    arguments={
                        # Claude Desktop few times returns stringified JSON
                        # for variables
                        "variables": '["wet_grass", "cloudy"]',
                        "evidence": {"rain": "yes", "sprinkler": "off"},
                    },
                ),
            )
        )

        content = assert_result_call(result)
        # Deserialize the content to assert the response
        jsonResult = json.loads(content.text)
        assert jsonResult == response_mock, (
            f"Expected: {response_mock} to match the received: {result}"
        )


@pytest.mark.asyncio
async def test_call_infer_tool_invalid_arg():
    response_mock = {"probabilities": {"no": 0.1, "yes": 0.9}}
    agent = GeniusAgent()

    with (
        patch.object(agent, "get_model_from_server", return_value=None),
        patch.object(agent, "infer", return_value=response_mock),
    ):
        agent_server = create_mcp_agent_server(GeniusMCPAgentAdapter(agent))

        handler = agent_server.request_handlers[types.CallToolRequest]
        result = await handler(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="infer",
                    arguments={
                        "variables": {"wet_grass": "invalid_type"},
                        "evidence": {"rain": "yes", "sprinkler": "off"},
                    },
                ),
            )
        )

        content = assert_result_call(result)
        assert content.text.find("Input should be a valid string") >= 0, (
            f"Expected error message to be in the content: {result}"
        )


@pytest.mark.asyncio
async def test_call_infer_tool_invalid_cmd():
    response_mock = {"probabilities": {"no": 0.1, "yes": 0.9}}
    agent = GeniusAgent()

    with (
        patch.object(agent, "get_model_from_server", return_value=None),
        patch.object(agent, "infer", return_value=response_mock),
    ):
        agent_server = create_mcp_agent_server(GeniusMCPAgentAdapter(agent))

        handler = agent_server.request_handlers[types.CallToolRequest]
        result = await handler(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="invalid_cmd",
                    arguments={
                        "variables": {"wet_grass": "invalid_type"},
                        "evidence": {"rain": True, "sprinkler": "off"},
                    },
                ),
            )
        )

        content = assert_result_call(result)
        assert content.text.find("Unknown tool") >= 0, (
            f"Expected error message to be in the content: {result}"
        )
