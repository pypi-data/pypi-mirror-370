import abc
import os
from typing import Collection, Dict, FrozenSet, Optional
import hyperlink

from .token_utils import TokenResponseData, get_app_access_token, get_application_token, get_delegated_app_access_token, get_extension_access_token, get_extension_identity_access_token


CONTENTGRID_HAL_CLIENT_LEEWAY = float(os.getenv("CONTENTGRID_HAL_CLIENT_LEEWAY", 5.0)) # seconds


class AuthenticationManager(abc.ABC):
    '''
    Abstract class to manage access tokens.
    Subclasses need to implement `for_url()` and `_fetch_access_token()`.
    '''
    def __init__(self, token_data: TokenResponseData | None = None, scope_hint: str | None = None, resources: Collection[str] = set(), leeway: float = CONTENTGRID_HAL_CLIENT_LEEWAY):
        self._token_data = token_data
        self._scope_hint = scope_hint
        normalized_resources = set(self._normalize_url(resource) for resource in resources)
        self._resources = frozenset(resource for resource in normalized_resources if resource is not None)
        self._origin = None

        if len(self._resources) > 0:
            self._origin = self._parse_origin(next(iter(self._resources)))
            # Check all origins are the same
            for resource in self._resources:
                if self._origin != self._parse_origin(resource):
                    raise ValueError(f"All resources should have the same origin: resource '{resource}' is not located at origin '{self._origin}'.")

        self.leeway = leeway
        self.valid = token_data is not None

    @property
    def access_token(self) -> Optional[str]:
        '''
        Get the access token, fetches a new one if expired or invalid.
        '''
        self.refresh(force=False)
        if self._token_data:
            return self._token_data.access_token
        else:
            return None

    @property
    def resources(self) -> FrozenSet[str]:
        '''
        Return the immutable resources of the access token.
        '''
        return self._resources

    @property
    def origin(self) -> str | None:
        '''
        Return the origin of the access token.
        '''
        return self._origin

    @property
    def scope_hint(self) -> str | None:
        '''
        Get the scope hint of the access token. It might be included when requesting an access token.
        '''
        return self._scope_hint

    def has_scope(self, value: str) -> bool:
        '''
        Returns whether the scope hint includes the given scope.
        '''
        if self.scope_hint is None:
            return False

        scopes_self = [val for val in self.scope_hint.split()]
        scopes = [val for val in value.split()]
        return all(val in scopes_self for val in scopes)

    def extend_scope(self, value: str) -> None:
        '''
        Extend the scope hint of the access token and mark access token invalid.
        '''
        if self.has_scope(value):
            return

        scopes = [val for val in value.split() if len(val) > 0 and not self.has_scope(val)]

        if self.scope_hint is None:
            self._scope_hint = str.join(' ', scopes)
        else:
            self._scope_hint = f"{self.scope_hint} {str.join(' ', scopes)}".strip()
        self.valid = False

    @abc.abstractmethod
    def for_url(self, url: str) -> "AuthenticationManager":
        '''
        Returns an AuthenticationManager for the url provided.
        '''
        pass

    @abc.abstractmethod
    def _fetch_access_token(self) -> "TokenResponseData":
        '''
        Fetches the access token.
        '''
        pass

    def _parse_origin(self, url: str) -> str | None:
        '''
        Parses the url and returns the origin of the url or None if it is a relative url.

        Parameters:
        - url: The url to be parsed.

        Examples:

        >>> print(auth_manager._parse_origin("https://www.example.com/test?foo=bar"))
        https://www.example.com
        >>> print(auth_manager._parse_origin("http://localhost:5432"))
        http://localhost:5432
        >>> print(auth_manager._parse_origin("/profile/customers"))
        None
        '''
        try:
            normalized_url = hyperlink.parse(url).normalize()
            if normalized_url.absolute:
                # Remove path, query parameters, fragment and userinfo.
                return normalized_url.replace(path=(), query=dict(), fragment="", userinfo="").to_text() # type: ignore
            else:
                return None  # Relative url
        except Exception:
            return None

    def _normalize_url(self, url: str) -> str | None:
        '''
        Returns the normalized version of the url if it is an absolute url, returns None otherwise.

        Parameters:
        - url: The url to be normalized.

        Examples:

        >>> print(auth_manager._normalize_url("https://WWW.Example.Com:443/test?foo=Bar"))
        https://www.example.com/test?foo=Bar
        >>> print(auth_manager._normalize_url("http://localhost:5432"))
        http://localhost:5432/
        >>> print(auth_manager._normalize_url("/profile/customers"))
        None
        '''
        try:
            normalized_url = hyperlink.parse(url).normalize()
            if normalized_url.absolute:
                return normalized_url.to_text()
            else:
                return None  # Relative url
        except Exception:
            return None

    def _is_expired(self) -> bool:
        '''
        Returns whether the access token needs to be refreshed because the token expired.
        '''
        if self._token_data:
            return self._token_data.is_expired(leeway=self.leeway)
        return True

    def refresh(self, force: bool = True) -> None:
        '''
        Refresh the access token.

        - force: Whether to force a refresh, even if current token is still valid (default: `True`).
        '''
        if force or not self.valid or self._is_expired():
            self._token_data = self._fetch_access_token()
            self.valid = True


class IdentityAuthenticationManager(AuthenticationManager):
    '''
    Manages the access token of the extensions realm, this token serves as the identity of the extension.
    Note that this token is only used to exchange it into access tokens of specific applications.
    '''
    def __init__(
            self,
            auth_uri: str,
            client_id: str,
            client_secret: str,
            system_exchange_uri: str,
            delegated_exchange_uri: str,
            leeway=CONTENTGRID_HAL_CLIENT_LEEWAY
    ):
        super().__init__(leeway=leeway)
        self.auth_uri = auth_uri
        self.client_id = client_id
        self.client_secret = client_secret
        self.system_exchange_uri = system_exchange_uri
        self.delegated_exchange_uri = delegated_exchange_uri
        self.system_cache: Dict[FrozenSet[str], SystemApplicationAuthenticationManager] = dict()

    def for_url(self, url: str) -> "AuthenticationManager":
        return self.for_application(urls=[url])

    def for_application(self, urls: Collection[str]) -> "ApplicationAuthenticationManager":
        '''
        Get a `SystemApplicationAuthenticationManager` for the given urls.
        It manages the system access token for the application urls.

        - urls: The absolute urls of the application to get access to.
        '''
        resource_set = set()
        for url in urls:
            resource = self._normalize_url(url)
            if not resource:
                raise ValueError(f"Absolute url is required, got {url}.")
            resource_set.add(resource)

        resources = frozenset(resource_set)
        auth_manager = self.system_cache.get(resources, None)

        if auth_manager:
            return auth_manager

        auth_manager = SystemApplicationAuthenticationManager(
            resources=resources,
            parent=self,
            exchange_uri=self.system_exchange_uri,
            leeway=self.leeway
        )

        # Save auth_manager in cache
        self.system_cache[resources] = auth_manager
        return auth_manager

    def for_user(self, user_token: str, urls: Collection[str]=set()) -> "ApplicationAuthenticationManager":
        '''
        Get a `DelegatedApplicationAuthenticationManager` for the given user token.
        It manages the user delegated access token of this user.

        - user_token: The access token of the user.
        - urls: The absolute urls of the application to get access to.
        '''
        if not user_token:
            raise ValueError("User token is required.")
        for url in urls:
            if not self._parse_origin(url):
                raise ValueError(f"Relative url is not allowed, got {url}.")

        auth_manager = DelegatedApplicationAuthenticationManager(
            resources=urls,
            parent=self,
            user_token=user_token,
            exchange_uri=self.delegated_exchange_uri,
            leeway=self.leeway
        )

        return auth_manager

    def _fetch_access_token(self) -> TokenResponseData:
        return get_extension_identity_access_token(auth_uri=self.auth_uri, client_id=self.client_id, client_secret=self.client_secret)


class ApplicationAuthenticationManager(AuthenticationManager):
    '''
    Abstract AuthenticationManager class for a runtime application.
    Subclasses still need to implement `_fetch_access_token()` from `AuthenticationManager`.
    '''
    def __init__(self, resources: Collection[str] = set(), parent: Optional["IdentityAuthenticationManager"] = None, extension_exchange_uri: str | None = None, leeway: float=CONTENTGRID_HAL_CLIENT_LEEWAY):
        super().__init__(resources=resources, leeway=leeway)
        self._parent = parent
        self.extension_exchange_uri = extension_exchange_uri if extension_exchange_uri \
                else f"{self.origin}/.contentgrid/authentication/external/token" if self.origin else None
        self.extension_cache: Dict[str, ExtensionAuthenticationManager] = dict()

    @property
    def parent(self) -> IdentityAuthenticationManager:
        '''
        Return the original `IdentityAuthenticationManager` used to construct this `ApplicationAuthenticationManager`.
        Raises `ValueError` if absent.
        '''
        if self._parent is None:
            raise ValueError("No parent provided.")
        return self._parent

    def for_url(self, url: str) -> "AuthenticationManager":
        if not self.origin or self._normalize_url(url) in self.resources:
            # Resource managed by this access token
            return self
        elif self.origin == self._parse_origin(url):
            # Same origin, url not managed by this access token
            return self.for_application(url)
        else:
            # Different origin, assume extension
            return self.for_extension(url)

    def for_application(self, url: str) -> "ApplicationAuthenticationManager":
        '''
        Get an `ApplicationAuthenticationManager` to manage an access token of an application with the same origin, but with different url.
        Returns `self` by default, subclasses may override this to provide a different `ApplicationAuthenticationManager`.

        - url: The url that resides on the same origin.
        '''
        return self

    def for_extension(self, url: str) -> "ExtensionAuthenticationManager":
        '''
        Get an `AuthenticationManager` to manage an access token of an extension with a different origin.

        -url: The url that resides on a different origin.
        '''
        if not self.extension_exchange_uri:
            raise ValueError("extension_exchange_uri is required.")
        origin = self._parse_origin(url)
        if not origin:
            raise ValueError(f"Absolute url is required, got {url}.")

        auth_manager = self.extension_cache.get(origin, None)

        if auth_manager:
            return auth_manager

        auth_manager = ExtensionAuthenticationManager(
            auth_uri=self.extension_exchange_uri,
            resources=[url],
            parent=self,
            leeway=self.leeway
        )

        # Save auth_manager in cache
        self.extension_cache[origin] = auth_manager
        return auth_manager


class PlainAccessTokenApplicationAuthenticationManager(ApplicationAuthenticationManager):
    '''
    Wrapper ApplicationAuthenticationManager for plain access tokens.
    '''
    def __init__(self, access_token: str, resources: Collection[str] = set(), extension_exchange_uri: str | None = None, leeway: float = CONTENTGRID_HAL_CLIENT_LEEWAY):
        super().__init__(resources=resources, parent=None, extension_exchange_uri=extension_exchange_uri, leeway=leeway)
        self._plain_access_token = access_token

    def _fetch_access_token(self) -> TokenResponseData:
        return TokenResponseData(self._plain_access_token, "unknown")


class ClientCredentialsApplicationAuthenticationManager(ApplicationAuthenticationManager):
    '''
    ApplicationAuthenticationManager with client credentials to the application.
    '''
    def __init__(self, auth_uri: str, client_id: str, client_secret: str, resources: Collection[str] = set(), extension_exchange_uri: str | None = None, leeway: float = CONTENTGRID_HAL_CLIENT_LEEWAY):
        super().__init__(resources=resources, parent=None, extension_exchange_uri=extension_exchange_uri, leeway=leeway)
        self.auth_uri = auth_uri
        self.client_id = client_id
        self.client_secret = client_secret

    def _fetch_access_token(self) -> TokenResponseData:
        return get_application_token(auth_uri=self.auth_uri, client_id=self.client_id, client_secret=self.client_secret)


class SystemApplicationAuthenticationManager(ApplicationAuthenticationManager):
    '''
    ApplicationAuthenticationManager for system access tokens.
    '''
    def __init__(self, parent: "IdentityAuthenticationManager", exchange_uri: str, resources: Collection[str], extension_exchange_uri: str | None = None, leeway: float=CONTENTGRID_HAL_CLIENT_LEEWAY):
        super().__init__(resources=resources, parent=parent, extension_exchange_uri=extension_exchange_uri, leeway=leeway)
        if len(self.resources) == 0:
            raise ValueError("At least one resource is required.")
        self.parent  # Raises if not provided
        self.exchange_uri = exchange_uri

    def _fetch_access_token(self) -> TokenResponseData:
        assert self.parent.access_token is not None, "Extention identity token is required"
        return get_app_access_token(exchange_uri=self.exchange_uri, extension_identity_token=self.parent.access_token, resource=self.resources)

    def for_application(self, url: str) -> "ApplicationAuthenticationManager":
        return self.parent.for_application(urls=[url])


class DelegatedApplicationAuthenticationManager(ApplicationAuthenticationManager):
    '''
    ApplicationAuthenticationManager for user delegated access tokens.
    '''
    def __init__(self, parent: "IdentityAuthenticationManager", user_token: str, exchange_uri: str, resources: Collection[str] = set(), extension_exchange_uri: str | None = None, leeway: float=CONTENTGRID_HAL_CLIENT_LEEWAY):
        super().__init__(resources=resources, parent=parent, extension_exchange_uri=extension_exchange_uri, leeway=leeway)
        self.parent  # Raises if not provided
        self.user_token = user_token
        self.exchange_uri = exchange_uri

    def _fetch_access_token(self) -> TokenResponseData:
        assert self.parent.access_token is not None, "Parent Access Token is required"
        return get_delegated_app_access_token(exchange_uri=self.exchange_uri, extension_identity_token=self.parent.access_token, user_access_token=self.user_token, resource=self.resources)

    def for_application(self, url: str) -> "ApplicationAuthenticationManager":
        return self.parent.for_user(self.user_token, urls=[url])


class ExtensionAuthenticationManager(AuthenticationManager):
    '''
    AuthenticationManager for accessing another extension.
    '''
    def __init__(self, auth_uri: str, resources: Collection[str] = set(), parent: "ApplicationAuthenticationManager | None"=None, leeway=CONTENTGRID_HAL_CLIENT_LEEWAY):
        super().__init__(resources=resources, leeway=leeway)
        self.auth_uri = auth_uri
        if len(self.resources) == 0:
            raise ValueError("At least one resource is required.")
        self.parent = parent

    def for_url(self, url: str) -> "AuthenticationManager":
        if self.origin == self._parse_origin(url):
            return self
        raise NotImplementedError("Not implemented")

    def _fetch_access_token(self) -> TokenResponseData:
        assert self.parent is not None, "Parent AuthManager is required"
        assert self.parent.access_token is not None, "Parent Access Token is required"
        return get_extension_access_token(exchange_uri=self.auth_uri, token=self.parent.access_token, resource=self.resources, scope=self.scope_hint)
