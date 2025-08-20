import logging
import os
import sys
from typing import Union

from genius_client_sdk.auth import ApiKeyConfig

SDK_AGENT_API_KEY = "SDK_AGENT_API_KEY"
SDK_AGENT_HTTP_PROTOCOL = "SDK_AGENT_HTTP_PROTOCOL"
SDK_AGENT_HOSTNAME = "SDK_AGENT_HOSTNAME"
SDK_AGENT_PORT = "SDK_AGENT_PORT"


def _get_auth_from_env() -> Union[ApiKeyConfig]:
    """
    Get the authentication configuration for the agent.

    Returns:
        Union[ApiKeyConfig, OAuth2BearerConfig, OAuth2ClientCredentialsConfig]: The authentication configuration.
    throws:
        SystemExit: If any of the required environment variables are missing or invalid.
    """

    api_key = os.getenv("SDK_AGENT_API_KEY")
    if api_key is not None:
        return ApiKeyConfig(api_key=api_key)

    logging.error(
        f"Missing authentication environment variable, supported types are: {', '.join([SDK_AGENT_API_KEY])}"
    )
    sys.exit(2)


def get_config_from_env() -> tuple[str, str, int, Union[ApiKeyConfig]]:
    """
    Get the configuration for the agent from environment variables.
    Returns:
        tuple[str, str, int, Union[ApiKeyConfig]]: A tuple containing the protocol, hostname, port, and authentication configuration.
    throws:
        SystemExit: If any of the required environment variables are missing or invalid.
    """

    protocol = os.getenv("SDK_AGENT_HTTP_PROTOCOL")
    hostname = os.getenv("SDK_AGENT_HOSTNAME")
    port = os.getenv("SDK_AGENT_PORT")

    auth = _get_auth_from_env()

    if protocol is None:
        logging.error(f"Missing environment variable: {SDK_AGENT_HTTP_PROTOCOL}")
        sys.exit(1)

    if hostname is None:
        logging.error(f"Missing environment variable: {SDK_AGENT_HOSTNAME}")
        sys.exit(1)

    if port is None:
        logging.error(f"Missing environment variable: {SDK_AGENT_PORT}")
        sys.exit(1)
    if port.isdigit() is False or int(port) < 0 or int(port) > 65535:
        logging.error(f"Invalid port number: {port}")
        sys.exit(1)

    return (protocol, hostname, int(port), auth)
