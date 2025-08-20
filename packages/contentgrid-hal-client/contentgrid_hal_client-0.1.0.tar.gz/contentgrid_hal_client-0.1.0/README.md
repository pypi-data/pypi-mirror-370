# HALFormsClient Library

## Overview

The `HALFormsClient` library provides a Python client for interacting with RESTful services that use the HAL (Hypertext Application Language) and HAL-Forms standards. This library simplifies the handling of HAL responses and their embedded resources, enabling easy navigation and interaction with APIs that follow the HAL and HAL-Forms specifications.

## Features

- Automatic token management for service accounts.
- Robust retry mechanisms for HTTP requests.
- Easy navigation of HAL links and embedded resources.
- Support for CURIEs (Compact URIs) for compacting and expanding link relations.
- Handling of common HTTP methods (`GET`, `POST`, `PATCH`, `DELETE`, `PUT`) with ease.
- Validation and transformation of HAL links and URIs.
- Customizable client configuration, including endpoint and authentication details.

## Installation

To install the library, use pip:

```bash
pip install contentgrid-hal-client
```

## Usage

### Initialization

To initialize the `HALFormsClient`, you need to provide the endpoint of the HAL service and optionally authentication details:

```python
from halformsclient import HALFormsClient

# Initialize using service account
client = HALFormsClient(
    client_endpoint="https://api.example.com",
    auth_uri="https://auth.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
)

# Initialize using bearer token
client = HALFormsClient(
    client_endpoint="https://api.example.com",
    auth_uri="https://auth.example.com",
    token="your_token"
)


# Initialize using session cookie
client = HALFormsClient(
    client_endpoint="https://api.example.com",
    auth_uri="https://auth.example.com",
    session_cookie="your_session_cookie"
)

```

### Fetching and Interacting with HAL Resources

You can fetch a HAL resource and interact with it using the provided methods:

```python
# Fetch a resource by following a link
resource = client.follow_link(HALLink(uri="/some/resource"))

# Access metadata
print(resource.metadata)

# Access links
links = resource.get_links("key")

# Access embedded resources
embedded_objects = resource.get_embedded_objects_by_key("embedded_key")

# Update a resource with PUT or PATCH
resource.put_data({"key": "value"})
resource.patch_data({"key": "new_value"})

# Delete a resource
resource.delete()
```

### Handling CURIEs

CURIEs (Compact URIs) are supported for compacting and expanding link relations:

```python
curie_registry = CurieRegistry(curies=[{"name": "ex", "href": "https://example.com/{rel}"}])
expanded_uri = curie_registry.expand_curie("ex:some_relation")
compact_uri = curie_registry.compact_curie("https://example.com/some_relation")
```

### Error Handling

The library provides custom exceptions for common HTTP errors:

```python
from halformsclient.exceptions import BadRequest, Unauthorized

try:
    resource = client.follow_link(HALLink(uri="/some/invalid/resource"))
except BadRequest as e:
    print(f"Bad request: {str(e)}")
except Unauthorized as e:
    print(f"Unauthorized: {str(e)}")
```