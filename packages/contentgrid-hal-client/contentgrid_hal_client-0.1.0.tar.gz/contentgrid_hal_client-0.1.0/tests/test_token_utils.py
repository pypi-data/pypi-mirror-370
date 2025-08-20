from requests.models import Response
from contentgrid_hal_client.token_utils import TokenRequestData, TokenResponseData, parse_authenticate_error, get_app_access_token, get_application_token, get_delegated_app_access_token, get_extension_access_token, get_extension_identity_access_token
from unittest.mock import patch, Mock


def test_parse_authenticate_error_in_header():
    response = Response()
    response.status_code = 401
    response.headers["WWW-Authenticate"] = (
        'Bearer realm="test", error="invalid_token", error_description="The access token expired"'
    )

    parsed = parse_authenticate_error(response)
    assert isinstance(parsed, dict)
    assert len(parsed) == 3
    assert parsed["error"] == "invalid_token"


def test_parse_authenticate_error_in_header_newlines():
    response = Response()
    response.status_code = 401
    response.headers["WWW-Authenticate"] = (
        'Bearer realm="test",\r\nerror="invalid_token",\r\nerror_description="The access token expired"'
    )

    parsed = parse_authenticate_error(response)
    assert isinstance(parsed, dict)
    assert len(parsed) == 3
    assert parsed["error"] == "invalid_token"


def test_parse_authenticate_error_invalid_status_code():
    response = Response()
    response.status_code = 404
    response.headers["WWW-Authenticate"] = (
        'Bearer realm="test", error="invalid_token", error_description="The access token expired"'
    )

    parsed = parse_authenticate_error(response)
    assert isinstance(parsed, dict)
    assert len(parsed) == 0


def test_parse_authenticate_error_missing_bearer():
    response = Response()
    response.status_code = 401
    response.headers["WWW-Authenticate"] = (
        'Basic realm="test", error="invalid_token", error_description="The access token expired"'
    )

    parsed = parse_authenticate_error(response)
    assert isinstance(parsed, dict)
    assert len(parsed) == 0


def test_parse_authenticate_error_empty_header():
    response = Response()
    response.status_code = 401
    response.headers["WWW-Authenticate"] = "Bearer"

    parsed = parse_authenticate_error(response)
    assert isinstance(parsed, dict)
    assert len(parsed) == 0


@patch.object(Response, 'json', return_value={
    "realm": "test",
    "error": "invalid_token",
    "error_description": "The access token expired"
})
def test_parse_authenticate_error_in_json(mock_json):
    response = Response()
    response.status_code = 401
    response.headers["WWW-Authenticate"] = "Bearer"
    response.headers["Content-Type"] = "application/json; charset=utf-8"

    parsed = parse_authenticate_error(response)
    assert mock_json.called
    assert isinstance(parsed, dict)
    assert len(parsed) == 3
    assert parsed["error"] == "invalid_token"


@patch.object(Response, 'json', return_value={
    "realm": "test",
    "error": "invalid_token",
    "error_description": "The access token expired"
})
def test_parse_authenticate_error_in_json_missing_header(mock_json):
    response = Response()
    response.status_code = 401
    response.headers["Content-Type"] = "application/json; charset=utf-8"

    parsed = parse_authenticate_error(response)
    assert not mock_json.called
    assert isinstance(parsed, dict)
    assert len(parsed) == 0


@patch.object(Response, 'json', return_value={
    "type": "http://localhost/test/invalid_token",
    "status": 401,
    "detail": "The access token expired"
})
def test_parse_authenticate_error_in_header_and_json(mock_json):
    response = Response()
    response.status_code = 401
    response.headers["WWW-Authenticate"] = (
        'Bearer realm="test", error="invalid_token", error_description="The access token expired"'
    )
    response.headers["Content-Type"] = "application/problem+json; charset=utf-8"

    parsed = parse_authenticate_error(response)
    assert not mock_json.called
    assert isinstance(parsed, dict)
    assert len(parsed) == 3
    assert parsed["error"] == "invalid_token"


@patch("contentgrid_hal_client.token_utils.request_token", return_value=TokenResponseData("access_token", "test"))
def test_get_application_token(mock_request_token: Mock):
    get_application_token(auth_uri="auth_uri", client_id="client_id", client_secret="client_secret")

    token_data = TokenRequestData(
        grant_type="client_credentials",
        client_id="client_id",
        client_secret="client_secret",
        scope="email",
    )

    mock_request_token.assert_called_once_with("auth_uri", token_data)


@patch("contentgrid_hal_client.token_utils.request_token", return_value=TokenResponseData("access_token", "test"))
def test_get_extension_identity_access_token(mock_request_token: Mock):
    get_extension_identity_access_token(auth_uri="auth_uri", client_id="client_id", client_secret="client_secret")

    token_data = TokenRequestData(
        grant_type="client_credentials",
        client_id="client_id",
        client_secret="client_secret",
    )

    mock_request_token.assert_called_once_with("auth_uri", token_data)


@patch("contentgrid_hal_client.token_utils.request_token", return_value=TokenResponseData("access_token", "test"))
def test_get_app_access_token(mock_request_token: Mock):
    get_app_access_token(exchange_uri="exchange_uri", extension_identity_token="extension_token", resource="resource")

    token_data = TokenRequestData(
        grant_type="urn:ietf:params:oauth:grant-type:token-exchange",
        subject_token="extension_token",
        subject_token_type="urn:ietf:params:oauth:token-type:access_token",
        resource="resource",
    )

    mock_request_token.assert_called_once_with("exchange_uri", token_data)


@patch("contentgrid_hal_client.token_utils.request_token", return_value=TokenResponseData("access_token", "test"))
def test_get_delegated_app_access_token_with_resource(mock_request_token: Mock):
    get_delegated_app_access_token(exchange_uri="exchange_uri", extension_identity_token="extension_token", user_access_token="user_token", resource="resource")

    token_data = TokenRequestData(
        grant_type="urn:ietf:params:oauth:grant-type:token-exchange",
        subject_token="user_token",
        subject_token_type="urn:ietf:params:oauth:token-type:access_token",
        actor_token="extension_token",
        actor_token_type="urn:ietf:params:oauth:token-type:access_token",
        resource="resource",
    )

    mock_request_token.assert_called_once_with("exchange_uri", token_data)


@patch("contentgrid_hal_client.token_utils.request_token", return_value=TokenResponseData("access_token", "test"))
def test_get_delegated_app_access_token_without_resource(mock_request_token: Mock):
    get_delegated_app_access_token(exchange_uri="exchange_uri", extension_identity_token="extension_token", user_access_token="user_token")

    token_data = TokenRequestData(
        grant_type="urn:ietf:params:oauth:grant-type:token-exchange",
        subject_token="user_token",
        subject_token_type="urn:ietf:params:oauth:token-type:access_token",
        actor_token="extension_token",
        actor_token_type="urn:ietf:params:oauth:token-type:access_token",
    )

    mock_request_token.assert_called_once_with("exchange_uri", token_data)


@patch("contentgrid_hal_client.token_utils.request_token", return_value=TokenResponseData("access_token", "test"))
def test_get_extension_access_token(mock_request_token: Mock):
    get_extension_access_token(exchange_uri="exchange_uri", token="token", resource="resource")

    token_data = TokenRequestData(
        grant_type="https://contentgrid.cloud/oauth2/grant/extension-token",
        resource="resource",
    )

    mock_request_token.assert_called_once_with("exchange_uri", token_data, extra_headers={"Authorization": "Bearer token"})


def test_token_response_data_expires_in():
    token_data = TokenResponseData(
        access_token="access_token",
        token_type="test",
        expires_in=60,
    )
    assert not token_data.is_expired()
    assert token_data.is_expired(leeway=60.0)


def test_token_response_data_without_expires_in():
    token_data = TokenResponseData(
        access_token="access_token",
        token_type="test",
    )
    assert not token_data.is_expired()
