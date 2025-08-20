from unittest import mock

import jwt
import pytest
import requests
from genius_client_sdk.auth import (
    ApiKeyConfig,
    AuthConfig,
    NoAuthConfig,
    OAuth2BearerConfig,
    OAuth2ClientCredentialsConfig,
    new_session_from_auth_config,
)
from requests.auth import AuthBase


@pytest.fixture
def api_key():
    return "test_api_key"


@pytest.fixture
def oauth_token():
    return jwt.encode(
        {
            "test_key": "test_value",
        },
        "test_secret",
        algorithm="HS256",
    )


@pytest.fixture
def client_id():
    return "test_client_id"


@pytest.fixture
def client_secret():
    return "test_client_secret"


@pytest.fixture
def access_token_response(oauth_token):
    return {
        "access_token": oauth_token,
        "token_type": "Bearer",
        "expires_in": 43199,
        "id_token": "some_id_token",
    }


def test_auth_no_auth():
    auth_config = NoAuthConfig()
    assert isinstance(auth_config, AuthConfig)
    assert auth_config.get_requests_auth() is None

    session = new_session_from_auth_config(auth_config)
    with mock.patch.object(session, "send", return_value=mock.MagicMock()):
        session.get("https://dumny-url.com")


def test_auth_api_key_init(api_key):
    auth_config = ApiKeyConfig(api_key=api_key)
    assert isinstance(auth_config, AuthConfig)
    assert auth_config.api_key == api_key


def test_auth_api_key_get_requests_auth(api_key):
    auth_config = ApiKeyConfig(api_key=api_key)
    auth = auth_config.get_requests_auth()
    assert isinstance(auth, AuthBase)


def test_auth_api_key_requests_session(api_key):
    auth_config = ApiKeyConfig(api_key=api_key)
    session = new_session_from_auth_config(auth_config)
    with mock.patch.object(session, "send") as mock_session_get:
        session.get("https://dumny-url.com")
        mock_session_get.assert_called_once()
        prepared_request_call = mock_session_get.call_args.args[0]
        prepared_request_call.headers["x-api-key"] == api_key


def test_auth_oauth2_bearer_init(oauth_token):
    auth_config = OAuth2BearerConfig(token=oauth_token)
    assert isinstance(auth_config, AuthConfig)
    assert auth_config.token == oauth_token


def test_auth_oauth2_bearer_get_requests_auth(oauth_token):
    auth_config = OAuth2BearerConfig(token=oauth_token)
    auth = auth_config.get_requests_auth()
    assert isinstance(auth, AuthBase)


def test_auth_oauth2_bearer_requests_session(oauth_token):
    auth_config = OAuth2BearerConfig(token=oauth_token)
    session = new_session_from_auth_config(auth_config)
    with mock.patch.object(session, "send") as mock_session_get:
        session.get("https://dumny-url.com")
        mock_session_get.assert_called_once()
        prepared_request_call = mock_session_get.call_args.args[0]
        prepared_request_call.headers["Authorization"] == f"Bearer {oauth_token}"


def test_auth_oauth2_client_credentials_init(client_id, client_secret):
    auth_config = OAuth2ClientCredentialsConfig(
        client_id=client_id, client_secret=client_secret
    )
    assert isinstance(auth_config, AuthConfig)
    assert auth_config.client_id == client_id
    assert auth_config.client_secret == client_secret


def test_auth_oauth2_client_credentials_get_requests_auth_valid(
    client_id, client_secret, access_token_response
):
    auth_config = OAuth2ClientCredentialsConfig(
        client_id=client_id, client_secret=client_secret
    )
    with mock.patch.object(requests.Session, "send") as mock_post_valid:
        mock_post_valid.return_value.status_code = 200
        mock_post_valid.return_value.json.return_value = access_token_response

        auth = auth_config.get_requests_auth()
        assert isinstance(auth, AuthBase)
        assert auth.token == access_token_response.get("access_token")


def test_auth_oauth2_client_credentials_get_requests_auth_exception_in_request(
    client_id, client_secret
):
    auth_config = OAuth2ClientCredentialsConfig(
        client_id=client_id, client_secret=client_secret
    )
    with mock.patch.object(
        requests.Session,
        "send",
    ) as mock_post_request_exception:
        mock_post_request_exception.side_effect = requests.exceptions.RequestException()
        with pytest.raises(RuntimeError):
            _ = auth_config.get_requests_auth()


def test_auth_oauth2_client_credentials_get_requests_auth_exception_in_json_decode(
    client_id, client_secret
):
    auth_config = OAuth2ClientCredentialsConfig(
        client_id=client_id, client_secret=client_secret
    )
    with mock.patch.object(
        requests.Session,
        "send",
    ) as mock_post_json_decode_exception:
        mock_post_json_decode_exception.return_value = requests.Response()
        mock_post_json_decode_exception.return_value.status_code = 200
        # causes requests to raise JSONDecodeError
        mock_post_json_decode_exception.return_value.data = "<!doctype html>"
        with pytest.raises(RuntimeError):
            _ = auth_config.get_requests_auth()


def test_auth_oauth2_client_credentials_get_requests_auth_malformed_response(
    client_id, client_secret
):
    auth_config = OAuth2ClientCredentialsConfig(
        client_id=client_id, client_secret=client_secret
    )
    with mock.patch.object(requests.Session, "send") as mock_post_malformed_response:
        mock_post_malformed_response.return_value.status_code = 200
        mock_post_malformed_response.return_value.json.return_value = {
            "some_invalid_key": "some_invalid_value"
        }
        with pytest.raises(RuntimeError):
            _ = auth_config.get_requests_auth()


def test_auth_oauth2_client_credentials_requests_session(
    client_id, client_secret, access_token_response
):
    auth_config = OAuth2ClientCredentialsConfig(
        client_id=client_id, client_secret=client_secret
    )
    # Create a real session or else it will be replaced with a mock.
    # This ensures that we can allow the full request to be built as intended
    real_session = requests.Session()
    with mock.patch.object(requests.Session, "post") as mock_post_valid:
        mock_post_valid.return_value.status_code = 200
        mock_post_valid.return_value.json.return_value = access_token_response
        session = new_session_from_auth_config(auth_config)
        real_session.auth = session.auth
        with mock.patch.object(real_session, "send") as mock_session_get:
            real_session.get("https://dumny-url.com")
            mock_session_get.assert_called_once()
            prepared_request_call = mock_session_get.call_args.args[0]
            prepared_request_call.headers[
                "Authorization"
            ] == f"Bearer {access_token_response.get('access_token')}"


def test_new_session_from_auth_config():
    auth_config = NoAuthConfig()
    assert (
        new_session_from_auth_config(auth_config).auth
        == auth_config.get_requests_auth()
    )
