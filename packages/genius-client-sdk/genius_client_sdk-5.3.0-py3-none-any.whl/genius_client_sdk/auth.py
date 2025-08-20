import abc
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from requests.auth import AuthBase

logger = logging.getLogger(__name__)


class AuthConfig(abc.ABC):
    @abc.abstractmethod
    def get_requests_auth(self) -> Optional[AuthBase]:
        """Get authentication mechanism for `requests` module"""

        pass


@dataclass
class NoAuthConfig(AuthConfig):
    """Default that represents no auth configuration."""

    def get_requests_auth(self):
        return None


@dataclass
class ApiKeyConfig(AuthConfig):
    api_key: str

    class ApiKeyAuth(AuthBase):
        def __init__(self, api_key: str):
            self.api_key = api_key

        def __call__(self, r):
            r.headers.update({"x-api-key": self.api_key})
            return r

    def get_requests_auth(self):
        return ApiKeyConfig.ApiKeyAuth(api_key=self.api_key)


@dataclass
class OAuth2BearerConfig(AuthConfig):
    token: str

    class OAuth2BearerAuth(AuthBase):
        def __init__(self, token: str):
            self.token = token

        def __call__(self, r):
            r.headers.update({"Authorization": f"Bearer {self.token}"})
            return r

    def get_requests_auth(self):
        return OAuth2BearerConfig.OAuth2BearerAuth(token=self.token)


@dataclass
class OAuth2ClientCredentialsConfig(AuthConfig):
    client_id: str
    client_secret: str

    def get_requests_auth(self):
        token_resp = OAuth2ClientCredentialsConfig.request_oauth_token(
            self.client_id, self.client_secret
        )
        token = token_resp.get("access_token")
        if token is None:
            raise RuntimeError("access token not found in auth response")
        return OAuth2BearerConfig.OAuth2BearerAuth(token=token)

    @staticmethod
    def request_oauth_token(
        client_id: str, client_secret: str, session: requests.Session = None
    ) -> Dict[str, Any]:
        """Authenticate using client id and secret and return the access token response"""

        if session is None:
            session = requests.Session()

        token_url = "https://zitadel.genius.dev.verses.build/oauth/v2/token"
        request_data = {
            "grant_type": "client_credentials",
            "scope": "openid profile urn:zitadel:iam:user:resourceowner",
        }

        try:
            response = session.post(
                token_url,
                data=request_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                auth=(client_id, client_secret),
            )
            response.raise_for_status()
            # oauth2 token response should always be json
            return response.json()
        # Ensure we handle the more specific subclass exception first
        except requests.exceptions.JSONDecodeError:
            logger.exception("Error decoding response from oauth token request")
            raise RuntimeError("error decoding response from oauth token request")
        except requests.exceptions.RequestException:
            logger.exception("Error during oauth token request")
            raise RuntimeError("error during oauth token request")


def new_session_from_auth_config(auth_config: AuthConfig) -> requests.Session:
    """Create a new `requests.Session` configured with the provided auth configuration."""

    session = requests.Session()
    session.auth = auth_config.get_requests_auth()
    return session
