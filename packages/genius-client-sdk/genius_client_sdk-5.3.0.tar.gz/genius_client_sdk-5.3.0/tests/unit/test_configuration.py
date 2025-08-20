import os

from genius_client_sdk.configuration import default_agent_config, BaseAgentConfig
from genius_client_sdk.agent import GeniusAgent
from genius_client_sdk.model import GeniusModel


def test_defaults():
    assert BaseAgentConfig.DEFAULT_AGENT_PORT == 3000
    assert BaseAgentConfig.DEFAULT_AGENT_HOSTNAME == "localhost"
    assert BaseAgentConfig.DEFAULT_AGENT_HTTP_PROTOCOL == "http"


def test_live_configuration():
    assert default_agent_config.agent_port == 3000
    assert default_agent_config.agent_hostname == "localhost"
    assert default_agent_config.agent_http_protocol == "http"
    assert default_agent_config.agent_url == "http://localhost:3000"


def test_envvar_configuration():
    # Set environment variables
    os.environ["AGENT_PORT"] = "2222"
    os.environ["AGENT_HOSTNAME"] = "remotehost"
    os.environ["AGENT_HTTP_PROTOCOL"] = "https"

    try:
        # get a new instance of config (sort of fakes a reload with new env vars)
        new_config = BaseAgentConfig()

        # verify
        assert new_config.agent_port == 2222
        assert new_config.agent_hostname == "remotehost"
        assert new_config.agent_http_protocol == "https"
        assert new_config.agent_url == "https://remotehost:2222"

        agent = GeniusAgent(
            agent_hostname=new_config.agent_hostname,
            agent_http_protocol=new_config.agent_http_protocol,
            agent_port=new_config.agent_port,
        )
        assert agent.agent_url == new_config.agent_url
        model = GeniusModel(agent_url=agent.agent_url)
        assert model.agent_url == new_config.agent_url

    finally:
        # clean up
        del os.environ["AGENT_PORT"]
        del os.environ["AGENT_HOSTNAME"]
        del os.environ["AGENT_HTTP_PROTOCOL"]
