import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


class BaseAgentConfig:
    """
    Configuration class to hold configuration values used by genius client sdk.
    """

    DEFAULT_AGENT_PORT: int = 3000
    """
    Default port number for the agent
    """

    DEFAULT_AGENT_HOSTNAME: str = "localhost"
    """
    Default hostname for the agent
    """

    DEFAULT_AGENT_HTTP_PROTOCOL: str = "http"
    """
    Default HTTP protocol for the agent
    """

    AGENT_URL_FORMAT = (
        "{self.agent_http_protocol}://{self.agent_hostname}:{self.agent_port}"
    )
    """Format string for the agent URL"""

    @property
    def agent_port(self) -> int:
        """Port number for the agent, defaulting to 3000 if not set in the environment"""
        return int(os.getenv("AGENT_PORT", BaseAgentConfig.DEFAULT_AGENT_PORT))

    @property
    def agent_hostname(self) -> str:
        """Hostname for the agent, defaulting to 'localhost' if not set in the environment"""
        return os.getenv("AGENT_HOSTNAME", BaseAgentConfig.DEFAULT_AGENT_HOSTNAME)

    @property
    def agent_http_protocol(self) -> str:
        """HTTP protocol for the agent, defaulting to 'http' if not set in the environment"""
        return os.getenv(
            "AGENT_HTTP_PROTOCOL", BaseAgentConfig.DEFAULT_AGENT_HTTP_PROTOCOL
        )

    @property
    def agent_url(self) -> str:
        """URL for the agent, constructed from the protocol, hostname, and port"""
        return BaseAgentConfig.AGENT_URL_FORMAT.format_map(locals())


default_agent_config = BaseAgentConfig()
