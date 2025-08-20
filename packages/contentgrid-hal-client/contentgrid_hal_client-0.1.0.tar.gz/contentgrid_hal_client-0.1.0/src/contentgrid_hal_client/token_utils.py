'''
Utilities for requesting and handling access tokens.
'''
from typing import Any, Collection, Dict
import requests as re
import json
import shlex
import time

class TokenRequestData:
    '''
    Token data for requesting an access token.

    - grant_type: The grant type of the token.
    - scope: The scope of the token.
    - resource: The URI or collection of URIs to get access to.
    - client_id: The client ID of the application.
    - client_secret: The client secret of the application.
    - subject_token: A token that represents the identity of the party on behalf of whom the request is being made.
    - subject_token_type: The type of token in the `subject_token` parameter.
    - actor_token: A token that represents the identity of the acting party. (Absent if actor is also subject.)
    - actor_token_type: The type of token in the `actor_token` parameter.
    '''
    def __init__(
            self,
            grant_type: str,
            scope: str | None=None,
            resource: str | Collection[str] | None=None,
            client_id: str | None=None,
            client_secret: str | None=None,
            subject_token: str | None=None,
            subject_token_type: str | None=None,
            actor_token: str | None=None,
            actor_token_type: str | None=None,
    ) -> None:
        '''
        Initialize a TokenData with the following parameters:

        - grant_type: The grant type of the token.
        - scope: The scope of the token.
        - resource: The URI or collection of URIs to get access to.
        - client_id: The client ID of the application.
        - client_secret: The client secret of the application.
        - subject_token: A token that represents the identity of the party on behalf of whom the request is being made.
        - subject_token_type: The type of token in the `subject_token` parameter.
        - actor_token: A token that represents the identity of the acting party. (Absent if actor is also subject.)
        - actor_token_type: The type of token in the `actor_token` parameter.
        '''
        self.grant_type = grant_type
        self.scope = scope
        self.resource = resource
        self.client_id = client_id
        self.client_secret = client_secret
        self.subject_token = subject_token
        self.subject_token_type = subject_token_type
        self.actor_token = actor_token
        self.actor_token_type = actor_token_type

    def to_dict(self) -> Dict[str, Any]:
        '''
        Get the token data as a dictionary.

        Returns the token data as a dictionary.
        '''
        data: Dict[str, Any] = {
            "grant_type": self.grant_type,
        }

        if self.scope:
            data["scope"] = self.scope
        if self.resource:
            data["resource"] = self.resource

        if self.client_id and self.client_secret:
            data["client_id"] = self.client_id
            data["client_secret"] = self.client_secret

        if self.subject_token is not None:
            data["subject_token"] = self.subject_token
            data["subject_token_type"] = self.subject_token_type

        if self.actor_token is not None:
            data["actor_token"] = self.actor_token
            data["actor_token_type"] = self.actor_token_type

        return data

    def __eq__(self, value):
        if isinstance(value, TokenRequestData):
            return self.to_dict() == value.to_dict()
        return False


class TokenResponseData:
    '''
    Token response data after requesting an access token.
    '''
    def __init__(
            self,
            access_token: str,
            token_type: str,
            expires_in: int | None = None,
            refresh_token: str | None = None,
            scope: str | None = None
    ):
        '''
        Initializes a TokenResponseData with following parameters:

        - access_token: The access token.
        - token_type: Type of access token.
        - expires_in: How long the token is valid (in seconds).
        - refresh_token: The refresh token used to refresh the access token (optional).
        - scope: The scope of the access token.
        '''
        self._start_time: float = time.time() # seconds since epoch
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.scope = scope

    def is_expired(self, leeway: float = 0.0) -> bool:
        '''
        Returns whether the token data is expired.

        - leeway: The number of seconds to substract from actual expiry.
        '''
        if self.expires_in is not None:
            return time.time() >= self._start_time + self.expires_in - leeway
        return False

    @classmethod
    def from_dict(cls, data: dict, scope: str | None = None):
        '''
        Construct a TokenResponseData object from a dictionary.

        - data: The dictionary containing the token response.
        - scope: The scope of the request (default scope if scope is not present in response).
        '''
        if "access_token" in data and isinstance(data["access_token"], str):
            access_token = data["access_token"]
        else:
            raise ValueError("access_token is required.")

        if "token_type" in data and isinstance(data["token_type"], str):
            token_type = data["token_type"]
        else:
            raise ValueError("token_type is required.")

        expires_in: int | None = data.get("expires_in", None)
        refresh_token: str | None = data.get("refresh_token", None)
        scope = data.get("scope", scope)

        return cls(access_token, token_type, expires_in=expires_in, refresh_token=refresh_token, scope=scope)


def request_token(uri: str, data: TokenRequestData, extra_headers: dict=dict()) -> TokenResponseData:
    '''
    Given a URI and token data, request an access token.

    - uri: The URI to request the access token from.
    - data: The token data to use for the request.

    Returns the access token.
    '''
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    for header, content in extra_headers.items():
        headers[header] = content

    res = re.post(uri, headers=headers, data=data.to_dict())

    if res.status_code != 200:
        error = parse_authenticate_error(res)
        reason = error.get("error_description", res.reason)
        raise Exception(f'Failed to request token. Status code: {res.status_code}. Reason: {reason}')
    else:
        return TokenResponseData.from_dict(res.json(), scope=data.scope)

def parse_authenticate_error(response: re.models.Response) -> dict:
    if response.status_code not in [400, 401, 403, 405]:
        return dict()
    if "www-authenticate" not in response.headers.keys() \
            or not response.headers["www-authenticate"].lower().startswith("bearer"):
        return dict()

    # try parsing header
    # e.g. 'Bearer realm="example", error="invalid_token", error_description="The access token expired"'
    #  -> {'realm': 'example', 'error': 'invalid_token', 'error_description': 'The access token expired'}
    header = response.headers["www-authenticate"]
    header = header[len("bearer"):].strip()
    lexer = shlex.shlex(header, posix=True)
    lexer.whitespace += "," # Treat ',' as whitespace instead of part of a word
    lexer.wordchars += "="  # Treat '=' as part of a word
    words = [word.split("=", maxsplit=1) for word in lexer]
    parsed_header = dict(values for values in words if len(values) == 2)

    if len(parsed_header) > 0:
        return parsed_header

    # try parsing body
    if "content-type" in response.headers.keys() and "json" in response.headers["content-type"]:
        try:
            parsed_body = response.json()
            if parsed_body is not None:
                return parsed_body
        except json.JSONDecodeError:
            pass

    return dict()


def get_application_token(auth_uri: str, client_id: str, client_secret: str) -> TokenResponseData:
    '''
    Get an application token for the given client ID and client secret.
    This only works if the extension has a service account on the application itself.

    - auth_uri: The authorization URI of the application.
    - client_id: The client ID of the application.
    - client_secret: The client secret of the application.

    Returns the application token.
    '''
    token_data = TokenRequestData(
        scope='email',
        grant_type='client_credentials',
        client_id=client_id,
        client_secret=client_secret
    )
    return request_token(auth_uri, token_data)


def get_extension_identity_access_token(auth_uri: str, client_id: str, client_secret: str) -> TokenResponseData:
    '''
    Get an access token of the extensions realm for the given client ID and client secret.
    This token can only be used to exchange it into access tokens of specific applications.

    - auth_uri: The authorization URI of the extensions realm.
    - client_id: The client ID of the application.
    - client_secret: The client secret of the application.

    Returns the identity token.
    '''
    token_data = TokenRequestData(
        grant_type='client_credentials',
        client_id=client_id,
        client_secret=client_secret
    )
    return request_token(auth_uri, token_data)


def get_delegated_app_access_token(exchange_uri: str, extension_identity_token: str, user_access_token: str, resource: str | Collection[str] | None=None) -> TokenResponseData:
    '''
    Get an extension delegated application access token for the given extension identity token and extension access token of the user.

    - exchange_uri: The exchange URI for extension delegated access tokens.
    - extension_identity_token: The access token of the extensions realm.
    - user_access_token: The extension access token of the user.
    - resource: The URI or collection of URIs to get access to.

    Returns the extension delegated application access token.
    '''
    token_data = TokenRequestData(
        grant_type="urn:ietf:params:oauth:grant-type:token-exchange",
        subject_token=user_access_token,
        subject_token_type="urn:ietf:params:oauth:token-type:access_token",
        actor_token=extension_identity_token,
        actor_token_type="urn:ietf:params:oauth:token-type:access_token",
        resource=resource
    )
    return request_token(exchange_uri, token_data)


def get_app_access_token(exchange_uri: str, extension_identity_token: str, resource: str | Collection[str]) -> TokenResponseData:
    '''
    Get an extension application access token for the given extension identity token and resource.

    - exchange_uri: The exchange URI for system access tokens.
    - extension_identity_token: The access token of the extensions realm.
    - resource: The URI or collection of URIs to get access to.

    Returns the extension application access token.
    '''
    assert resource is not None and len(resource) > 0, "resource is required"

    token_data = TokenRequestData(
        grant_type="urn:ietf:params:oauth:grant-type:token-exchange",
        subject_token=extension_identity_token,
        subject_token_type="urn:ietf:params:oauth:token-type:access_token",
        resource=resource
    )
    return request_token(exchange_uri, token_data)


def get_extension_access_token(exchange_uri: str, token: str, resource: str | Collection[str], scope: str | None=None) -> TokenResponseData:
    '''
    Get an extension application access token for the given (delegated) application access token and resource.
    Only necessary if the extension wants to call another extension.

    - exchange_uri: The extension exchange URI of the application.
    - token: The application access token or the delegated application access token of the extension.
    - resource: The URI or collection of URIs to get access to.
    - scope: The scope of the token.

    Returns the extension application access token.
    '''
    assert resource is not None and len(resource) > 0, "resource is required"

    token_data = TokenRequestData(
        scope=scope,
        grant_type="https://contentgrid.cloud/oauth2/grant/extension-token",
        resource=resource
    )

    extra_headers = { "Authorization": f"Bearer {token}" }
    return request_token(exchange_uri, token_data, extra_headers=extra_headers)
