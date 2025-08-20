import os
from dotenv import load_dotenv
import pytest
from contentgrid_hal_client import HALFormsClient, HALResponse, InteractiveHALResponse, HALLink, CurieRegistry
from contentgrid_hal_client.security import ApplicationAuthenticationManager, ClientCredentialsApplicationAuthenticationManager
from unittest.mock import patch, MagicMock

load_dotenv(override=True)
load_dotenv(".env.secret", override=True)

CONTENTGRID_CLIENT_ENDPOINT = os.getenv("CONTENTGRID_CLIENT_ENDPOINT")
CONTENTGRID_AUTH_URI = os.getenv("CONTENTGRID_AUTH_URI")
CONTENTGRID_EXTENSION_EXCHANGE_URI = os.getenv("CONTENTGRID_EXTENSION_EXCHANGE_URI")

# Service account
CONTENTGRID_CLIENT_ID = os.getenv("CONTENTGRID_CLIENT_ID")
CONTENTGRID_CLIENT_SECRET = os.getenv("CONTENTGRID_CLIENT_SECRET")


@pytest.fixture
def auth_manager():
    return ClientCredentialsApplicationAuthenticationManager(
        resources=[CONTENTGRID_CLIENT_ENDPOINT],
        auth_uri=CONTENTGRID_AUTH_URI,
        client_id=CONTENTGRID_CLIENT_ID,
        client_secret=CONTENTGRID_CLIENT_SECRET,
        extension_exchange_uri=CONTENTGRID_EXTENSION_EXCHANGE_URI
    )

@pytest.fixture
def hal_client(auth_manager: ApplicationAuthenticationManager):
    return HALFormsClient(
        client_endpoint=CONTENTGRID_CLIENT_ENDPOINT,
        auth_manager=auth_manager
    )


def test_hal_client_initialization(hal_client: HALFormsClient):
    assert hal_client.client_endpoint.to_text() == CONTENTGRID_CLIENT_ENDPOINT + ("" if CONTENTGRID_CLIENT_ENDPOINT.endswith("/") else "/")
    assert isinstance(hal_client.auth_manager, ApplicationAuthenticationManager)
    assert hal_client.headers["Accept"] == "application/prs.hal-forms+json"


def test_hal_link():
    link = HALLink(uri="https://api.example.com/resource", name="resource", title="Resource")
    assert link.uri == "https://api.example.com/resource"
    assert link.name == "resource"
    assert link.title == "Resource"


def test_curie_registry():
    curies = [{"name": "ex", "href": "https://api.example.com/rels/{rel}"}]
    registry = CurieRegistry(curies)
    expanded = registry.expand_curie("ex:resource")
    assert expanded == "https://api.example.com/rels/resource"
    compacted = registry.compact_curie("https://api.example.com/rels/resource")
    assert compacted == "ex:resource"


def test_hal_response_initialization():
    data = {
        "_links": {
            "self": {"href": "https://api.example.com/resource"},
            "curies": [{"name": "ex", "href": "https://api.example.com/rels/{rel}"}]
        },
        "_embedded": {},
        "_templates": {},
        "metadata": "value"
    }
    response = HALResponse(data)
    assert response.data == data
    assert response.links == data["_links"]
    assert response.embedded == data["_embedded"]
    assert response.templates == data["_templates"]
    assert response.metadata == {"metadata": "value"}


def test_hal_response_has_link():
    data = {
        "_links": {
            "self": {"href": "https://api.example.com/resource"}
        }
    }
    response = HALResponse(data)
    assert response.has_link("self") is True
    assert response.has_link("nonexistent") is False


def test_hal_response_get_link():
    data = {
        "_links": {
            "self": {"href": "https://api.example.com/resource"}
        }
    }
    response = HALResponse(data)
    link = response.get_link("self")
    assert link.uri == "https://api.example.com/resource"
    assert response.get_link("nonexistent") is None


def test_hal_response_get_links():
    data = {
        "_links": {
            "self": {"href": "https://api.example.com/resource"},
            "multiple": [
                {"href": "https://api.example.com/resource1"},
                {"href": "https://api.example.com/resource2"}
            ]
        }
    }
    response = HALResponse(data)
    links = response.get_links("multiple")
    assert len(links) == 2
    assert links[0].uri == "https://api.example.com/resource1"
    assert links[1].uri == "https://api.example.com/resource2"


@patch.object(HALFormsClient, 'request', return_value=MagicMock(status_code=200, json=lambda: {}))
def test_interactive_hal_response_refetch(mock_request, hal_client: HALFormsClient):
    data = {
        "_links": {
            "self": {"href": "https://api.example.com/resource"}
        }
    }
    response = InteractiveHALResponse(data, hal_client)
    response.refetch()
    assert mock_request.called
    assert mock_request.call_args[0] == ('GET', 'https://api.example.com/resource')


@patch.object(HALFormsClient, 'request', return_value=MagicMock(status_code=204))
def test_interactive_hal_response_delete(mock_request, hal_client: HALFormsClient):
    data = {
        "_links": {
            "self": {"href": "https://api.example.com/resource"}
        }
    }
    response = InteractiveHALResponse(data, hal_client)
    response.delete()
    assert mock_request.called
    assert mock_request.call_args[0] == ('DELETE', 'https://api.example.com/resource')


@patch.object(HALFormsClient, 'request', return_value=MagicMock(status_code=200, json=lambda: {}))
def test_interactive_hal_response_put_data(mock_request, hal_client: HALFormsClient):
    data = {
        "_links": {
            "self": {"href": "https://api.example.com/resource"}
        }
    }
    response = InteractiveHALResponse(data, hal_client)
    new_data = {"key": "value"}
    response.put_data(new_data)
    assert mock_request.called
    assert mock_request.call_args[0] == ('PUT', 'https://api.example.com/resource')
    assert mock_request.call_args[1]['json'] == new_data


@patch.object(HALFormsClient, 'request', return_value=MagicMock(status_code=200, json=lambda: {}))
def test_interactive_hal_response_patch_data(mock_request, hal_client: HALFormsClient):
    data = {
        "_links": {
            "self": {"href": "https://api.example.com/resource"}
        }
    }
    response = InteractiveHALResponse(data, hal_client)
    new_data = {"key": "value"}
    response.patch_data(new_data)
    assert mock_request.called
    assert mock_request.call_args[0] == ('PATCH', 'https://api.example.com/resource')
    assert mock_request.call_args[1]['json'] == new_data
