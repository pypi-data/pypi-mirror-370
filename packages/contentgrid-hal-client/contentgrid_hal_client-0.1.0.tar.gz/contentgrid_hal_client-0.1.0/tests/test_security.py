from typing import Any, Generator
import pytest
from unittest import mock

from contentgrid_hal_client.security import (
    ApplicationAuthenticationManager,
    ClientCredentialsApplicationAuthenticationManager,
    IdentityAuthenticationManager,
    PlainAccessTokenApplicationAuthenticationManager,
)
from contentgrid_hal_client.token_utils import TokenResponseData


CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
APP_AUTH_URI = "app_auth_uri"
IDENTITY_AUTH_URI = "identity_auth_uri"
SYSTEM_EXCHANGE_URI = "system_exchange_uri"
DELEGATED_EXCHANGE_URI = "delegated_exchange_uri"
EXTENSION_EXCHANGE_URI = "extension_exchange_uri"
APP_ENDPOINT = "http://localhost:8080"
EXTENSION_ENDPOINT = "http://localhost:5003"
EXTENSION_RESOURCE = f"{EXTENSION_ENDPOINT}/test/mock"
RESOURCES = frozenset((f"{APP_ENDPOINT}/profile", f"{APP_ENDPOINT}/profile/customers", f"{APP_ENDPOINT}/customers"))
USER_TOKEN = "user_token"
PLAIN_TOKEN = "plain_token"


def get_token_data1():
    return TokenResponseData(access_token=PLAIN_TOKEN, token_type="test", expires_in=60)


def get_token_data2():
    return TokenResponseData(access_token=PLAIN_TOKEN + "_test", token_type="test", expires_in=30, scope="test")


def get_token_data3():
    return TokenResponseData(access_token="extension_token", token_type="test", expires_in=30, scope="test")


def get_expired_token_data():
    return TokenResponseData(access_token="expired_token", token_type="test", expires_in=-10)


######################## TEST FIXTURES #########################

@pytest.fixture
def mock_identity_access_token() -> Generator[mock.Mock, Any, None]:
    # Using 'security' instead of 'token_utils', because that is the location that is looked up by 'IdentityAuthenticationManager'
    # See https://docs.python.org/3/library/unittest.mock.html#id6
    with mock.patch("contentgrid_hal_client.security.get_extension_identity_access_token", return_value=get_token_data1()) as obj:
        yield obj


@pytest.fixture
def mock_system_access_token() -> Generator[mock.Mock, Any, None]:
    with mock.patch("contentgrid_hal_client.security.get_app_access_token", return_value=get_token_data2()) as obj:
        yield obj


@pytest.fixture
def mock_delegated_access_token() -> Generator[mock.Mock, Any, None]:
    with mock.patch("contentgrid_hal_client.security.get_delegated_app_access_token", return_value=get_token_data2()) as obj:
        yield obj


@pytest.fixture
def mock_credentials_access_token() -> Generator[mock.Mock, Any, None]:
    with mock.patch("contentgrid_hal_client.security.get_application_token", return_value=get_token_data2()) as obj:
        yield obj


@pytest.fixture
def mock_extension_access_token() -> Generator[mock.Mock, Any, None]:
    with mock.patch("contentgrid_hal_client.security.get_extension_access_token", return_value=get_token_data3()) as obj:
        yield obj


@pytest.fixture
def identity_auth_manager() -> IdentityAuthenticationManager:
    return IdentityAuthenticationManager(
            auth_uri=IDENTITY_AUTH_URI,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            system_exchange_uri=SYSTEM_EXCHANGE_URI,
            delegated_exchange_uri=DELEGATED_EXCHANGE_URI,
        )


@pytest.fixture
def system_auth_manager(identity_auth_manager: IdentityAuthenticationManager) -> ApplicationAuthenticationManager:
    return identity_auth_manager.for_application(RESOURCES)


@pytest.fixture
def delegated_auth_manager(identity_auth_manager: IdentityAuthenticationManager) -> ApplicationAuthenticationManager:
    return identity_auth_manager.for_user(USER_TOKEN)


@pytest.fixture
def client_credentials_auth_manager() -> ApplicationAuthenticationManager:
    return ClientCredentialsApplicationAuthenticationManager(
            auth_uri=APP_AUTH_URI,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            extension_exchange_uri=EXTENSION_EXCHANGE_URI,
        )


@pytest.fixture
def plain_access_token_auth_manager() -> ApplicationAuthenticationManager:
    return PlainAccessTokenApplicationAuthenticationManager(
        access_token=PLAIN_TOKEN,
        extension_exchange_uri=EXTENSION_EXCHANGE_URI,
    )

########################## UNIT TESTS ##########################

# See https://en.wikipedia.org/wiki/URI_normalization
@pytest.mark.parametrize("url,expected", [
    ("http://example.com/foo%2a", "http://example.com/foo%2A"),
    ("HTTP://User@Example.COM/Foo", "http://User@example.com/Foo"),
    ("http://example.com/%7Efoo", "http://example.com/~foo"),
    ("http://example.com/foo/./bar/baz/../qux", "http://example.com/foo/bar/qux"),
    ("http://example.com:80", "http://example.com/"),
    ("/foo/bar", None),
    (None, None),
])
def test_normalize_url(url: str, expected: str, plain_access_token_auth_manager: ApplicationAuthenticationManager):
    assert plain_access_token_auth_manager._normalize_url(url) == expected


@pytest.mark.parametrize("url,expected", [
    ("http://example.com/foo%2a", "http://example.com"),
    ("HTTP://User@Example.COM/Foo", "http://example.com"),
    ("http://example.com/%7Efoo", "http://example.com"),
    ("http://example.com/foo/./bar/baz/../qux", "http://example.com"),
    ("http://example.com:80", "http://example.com"),
    ("/foo/bar", None),
    (None, None),
])
def test_parse_origin(url: str, expected: str, plain_access_token_auth_manager: ApplicationAuthenticationManager):
    assert plain_access_token_auth_manager._parse_origin(url) == expected


@pytest.mark.parametrize("initial,scope,expected", [
    ("app:read", "app:write", "app:read app:write"),
    ("app:read", "app:read app:write", "app:read app:write"),
    ("app:read app:write", "app:write", "app:read app:write"),
    ("app:read", "app:read:1", "app:read app:read:1"),
    ("app:read:1", "app:read", "app:read:1 app:read"),
])
def test_extend_scope(initial: str, scope: str, expected: str, plain_access_token_auth_manager: ApplicationAuthenticationManager):
    assert plain_access_token_auth_manager.scope_hint is None
    plain_access_token_auth_manager.extend_scope(initial)
    assert plain_access_token_auth_manager.scope_hint == initial
    assert plain_access_token_auth_manager.has_scope(initial)
    plain_access_token_auth_manager.extend_scope(scope)
    assert plain_access_token_auth_manager.scope_hint == expected
    assert plain_access_token_auth_manager.has_scope(initial)
    assert plain_access_token_auth_manager.has_scope(scope)


def test_is_expired_of_new_token(plain_access_token_auth_manager: ApplicationAuthenticationManager):
    with mock.patch.object(PlainAccessTokenApplicationAuthenticationManager, "_fetch_access_token", return_value=get_token_data2()):
        assert plain_access_token_auth_manager._is_expired()
        plain_access_token_auth_manager.access_token # fetch new token
        assert not plain_access_token_auth_manager._is_expired()


def test_is_expired_of_expired_token(plain_access_token_auth_manager: ApplicationAuthenticationManager):
    with mock.patch.object(PlainAccessTokenApplicationAuthenticationManager, "_fetch_access_token", return_value=get_expired_token_data()):
        assert plain_access_token_auth_manager._is_expired()
        plain_access_token_auth_manager.access_token # fetch expired token
        assert plain_access_token_auth_manager._is_expired()

###################### INTEGRATION TESTS #######################

def test_identity_auth_manager(mock_identity_access_token: mock.Mock, identity_auth_manager: IdentityAuthenticationManager):
    mock_identity_access_token.assert_not_called()

    assert identity_auth_manager.access_token == get_token_data1().access_token

    mock_identity_access_token.assert_called_once_with(auth_uri=IDENTITY_AUTH_URI, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


def test_system_auth_manager(mock_identity_access_token: mock.Mock, mock_system_access_token: mock.Mock, system_auth_manager: ApplicationAuthenticationManager):
    mock_identity_access_token.assert_not_called()
    mock_system_access_token.assert_not_called()

    assert system_auth_manager.access_token == get_token_data2().access_token

    mock_identity_access_token.assert_called_once_with(auth_uri=IDENTITY_AUTH_URI, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    mock_system_access_token.assert_called_once_with(exchange_uri=SYSTEM_EXCHANGE_URI, extension_identity_token=get_token_data1().access_token, resource=RESOURCES)


def test_delegated_auth_manager(mock_identity_access_token: mock.Mock, mock_delegated_access_token: mock.Mock, delegated_auth_manager: ApplicationAuthenticationManager):
    mock_identity_access_token.assert_not_called()
    mock_delegated_access_token.assert_not_called()

    assert delegated_auth_manager.access_token == get_token_data2().access_token

    mock_identity_access_token.assert_called_once_with(auth_uri=IDENTITY_AUTH_URI, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    mock_delegated_access_token.assert_called_once_with(exchange_uri=DELEGATED_EXCHANGE_URI, extension_identity_token=get_token_data1().access_token, user_access_token=USER_TOKEN, resource=frozenset())


def test_credentials_auth_manager(mock_credentials_access_token: mock.Mock, client_credentials_auth_manager: ApplicationAuthenticationManager):
    mock_credentials_access_token.assert_not_called()

    assert client_credentials_auth_manager.access_token == get_token_data2().access_token

    mock_credentials_access_token.assert_called_once_with(auth_uri=APP_AUTH_URI, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


def test_extension_auth_manager(mock_identity_access_token: mock.Mock, mock_system_access_token: mock.Mock, mock_extension_access_token: mock.Mock, system_auth_manager: ApplicationAuthenticationManager):
    extension_auth_manager = system_auth_manager.for_url(EXTENSION_RESOURCE)
    assert extension_auth_manager is not system_auth_manager

    mock_identity_access_token.assert_not_called()
    mock_system_access_token.assert_not_called()
    mock_extension_access_token.assert_not_called()

    assert extension_auth_manager.access_token == get_token_data3().access_token

    mock_identity_access_token.assert_called_once_with(auth_uri=IDENTITY_AUTH_URI, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    mock_system_access_token.assert_called_once_with(exchange_uri=SYSTEM_EXCHANGE_URI, extension_identity_token=get_token_data1().access_token, resource=RESOURCES)
    mock_extension_access_token.assert_called_once_with(exchange_uri=f"{APP_ENDPOINT}/.contentgrid/authentication/external/token", token=get_token_data2().access_token, resource=frozenset((EXTENSION_RESOURCE,)), scope=None)
