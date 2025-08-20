from json import JSONDecodeError
import json
import logging
import re
from typing import List, Optional, Type, TypeVar, cast
from contentgrid_hal_client.hal_forms import HALFormsTemplate
import hyperlink
import uri_template
import requests
from requests.adapters import Retry, HTTPAdapter
from pydantic import BaseModel, Field
from .token_utils import parse_authenticate_error
from .exceptions import BadRequest, MissingHALTemplate
from .security import AuthenticationManager, PlainAccessTokenApplicationAuthenticationManager, ClientCredentialsApplicationAuthenticationManager


class HALLink(BaseModel):
    name : Optional[str] = None
    title : Optional[str] = None
    uri: str = Field(..., serialization_alias="href", exclude=False)
    link_relation: Optional[str] = None
    templated: bool = False

    def expand_template(self, **kwargs) -> str:
        """
        Expand the URI template with the provided variables.
        
        Args:
            **kwargs: Variables to use for template expansion
            
        Returns:
            The expanded URI
        """
        if not self.templated:
            return self.uri
        
        return str(uri_template.URITemplate(self.uri).expand(**kwargs))

class HALShape(BaseModel):
    links: dict[str, HALLink] = Field(serialization_alias="_links")
    templates: Optional[dict[str, HALFormsTemplate]] = Field(serialization_alias="_templates", default_factory=dict)
    embedded: Optional[dict[str, List[dict]]] = Field(serialization_alias="_embedded", default=None, exclude=True)
    
class CurieRegistry:
    def __init__(self, curies: List[dict]) -> None:
        self.curies = {
            curie["name"]: Curie(curie["name"], curie["href"]) for curie in curies
        }

    def expand_curie(self, rel):
        if ":" in rel:
            prefix, suffix = rel.split(":", 1)
            if prefix in self.curies.keys():
                return uri_template.URITemplate(self.curies[prefix].url_template).expand(
                    rel=suffix
                )
        return rel

    def compact_curie(self, link: str):
        for curie in self.curies.values():
            variable_names = re.findall(r'{(.*?)}', curie.url_template)
            pattern = re.sub(r'{(.*?)}', r'(?P<\g<1>>.+)',  curie.url_template)
            match = re.match(pattern, link)
            if match:
                extracted_values = match.groupdict()
                variable_map = {variable_names[i]: extracted_values[variable_names[i]] for i in range(len(variable_names))}
                if "rel" in variable_map.keys():
                    return f"{curie.prefix}:{variable_map['rel']}"
        return link

class Curie:
    def __init__(self, prefix: str, url_template: str) -> None:
        assert uri_template.validate(template=url_template)
        self.url_template = url_template
        self.url_prefix = str(uri_template.URITemplate(url_template).expand(rel=''))
        self.prefix = prefix

class HALResponse:
    def __init__(self, data: dict, curie_registry: CurieRegistry = None) -> None:
        self.data: dict = data
        self.links: Optional[dict] = cast(Optional[dict], data.get("_links", None))
        if self.links and "curies" in self.links.keys():
            self.curie_registry: CurieRegistry = CurieRegistry(self.links["curies"])
        elif curie_registry is not None:
            self.curie_registry = curie_registry
        else:
            self.curie_registry = CurieRegistry(curies=[])

        self.embedded: Optional[dict] = cast(Optional[dict], data.get("_embedded", None))
        
        if "_templates" in data.keys():
            self.templates: dict[str, HALFormsTemplate] = {template_name : HALFormsTemplate(**value) for template_name, value in data["_templates"].items()}
        else:
            self.templates = {}
        
        self.metadata = {
            key: value
            for key, value in data.items()
            if not key.startswith("_")
        }

    def has_link(self, linkrel : str) -> bool:
        return len(self.get_links(linkrel=linkrel)) > 0

    def get_link(self, linkrel: str) -> Optional[HALLink]:
        if not self.links:
            return None
        if self.has_link(linkrel=linkrel):
            if linkrel in self.links.keys():
                value = self.links[linkrel]
                if isinstance(value, list):
                    raise Exception(f"Linkrel {linkrel} was multivalued. Use get_links instead.")
            return self.get_links(linkrel=linkrel)[0]
        else:
            return None

    def get_links(self, linkrel: str) -> List[HALLink]:
        if not self.links:
            return []
        full_linkrel = linkrel
        # compact linkrel if curie registry is available.
        if self.curie_registry:
            linkrel = self.curie_registry.compact_curie(linkrel)

        if linkrel in self.links.keys():
            value = self.links[linkrel]
            if isinstance(value, list):
                return [
                    HALLink(
                        name=v.get("name", None),
                        title=v.get("title", None),
                        uri=v["href"],
                        link_relation=full_linkrel,
                        templated=v.get("templated", False)
                    )
                    for v in value
                ]
            elif isinstance(value, dict):
                return [
                    HALLink(
                        name=value.get("name", None),
                        title=value.get("title", None),
                        uri=value["href"],
                        link_relation=full_linkrel,
                        templated=value.get("templated", False)
                    )
                ]

            else:
                raise Exception(f"Unkown HALLINK type {type(value)}")
        else:
            return []

    def get_embedded_objects_by_key(self, key : str, infer_type:type = None) -> List["HALResponse"]:
        if self.embedded:
            if not infer_type:
                infer_type = HALResponse
            return [
                infer_type(data=v, curie_registry=self.curie_registry)
                for v in self.embedded[self.curie_registry.compact_curie(key)]
            ]
        else:
            return []

    def get_self_link(self) -> HALLink:
        self_link = self.get_link("self")
        assert self_link is not None, "Expected self link but was not present."
        return self_link

    def get_template(self, template_name : str) -> HALFormsTemplate:
        if self.templates and template_name in self.templates.keys():
            return self.templates[template_name]
        else:
            raise MissingHALTemplate(f"HALForms template : {template_name} not found. User might not have permission or resource is of imcompatible type.")

    def __str__(self) -> str:
        return json.dumps(self.data, indent=4)

class InteractiveHALResponse(HALResponse):
    def __init__(self, data: dict, client: "HALFormsClient", curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, curie_registry)
        self.client : "HALFormsClient" = client

    T = TypeVar('T', bound=HALResponse)
    def get_embedded_objects_by_key(self, key, infer_type:Type[T] = None) -> List[T]:
        if self.embedded:
            if not infer_type:
                infer_type = InteractiveHALResponse # type: ignore

            if issubclass(infer_type, InteractiveHALResponse): # type: ignore
                return [
                    infer_type(data=v, client=self.client, curie_registry=self.curie_registry) # type: ignore
                    for v in self.embedded[self.curie_registry.compact_curie(key)]
                ]
            else:
                return [
                    infer_type(data=v, curie_registry=self.curie_registry) # type: ignore
                    for v in self.embedded[self.curie_registry.compact_curie(key)]
                ]
        else:
            return []

    # Common operations
    def refetch(self):
        response = self.client.follow_link(self.get_self_link())
        self.__init__(data=response.data, client=self.client, curie_registry=self.curie_registry)

    def delete(self):
        response = self.client.delete(self.get_self_link().uri)
        self.client._validate_non_json_response(response)

    def put_data(self, data : dict) -> None:
        response = self.client.put(self.get_self_link().uri, json=data, headers={"Content-Type" : "application/json"})
        reponse_data = self.client._validate_json_response(response)
        if isinstance(reponse_data, dict):
            # Reinitialize class based on response data
            self.__init__(data=reponse_data, client=self.client, curie_registry=self.curie_registry) # type: ignore
        else:
            # Reinitialize class by fetching self link
            self.refetch()

    def patch_data(self, data : dict) -> None:
        response = self.client.patch(self.get_self_link().uri, json=data, headers={"Content-Type" : "application/json"})
        response_data = self.client._validate_json_response(response)
        if isinstance(response_data, dict):
            # Reinitialize class based on response data
            self.__init__(data=response_data, client=self.client, curie_registry=self.curie_registry) # type: ignore
        else:
            # Reinitialize class by fetching self link
            self.refetch()


class HALFormsClient(requests.Session):
    def __init__(self,
        client_endpoint: str,
        auth_uri: str | None = None,
        auth_manager: AuthenticationManager | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        token: str | None = None,
        session_cookie : str | None = None,
        pool_maxsize : int = 10,
    ) -> None:
        '''
        Initializes a HALFormsClient.

        - client_endpoint: The contentgrid application endpoint.
        - auth_uri: The user authentication endpoint of the application.
        - auth_manager: The authentication manager that provides access tokens.
        - client_id: The client id of the extension.
        - client_secret: The client secret of the extension.
        - token: The (delegated) access token of the application.
        - session_cookie: The SESSION cookie, will use cookie-based authorization instead of access tokens if present.
        - pool_maxsize: Maximum number of connections to save in HTTP connection pool.
        '''
        super().__init__()
        self.session_cookie = session_cookie.replace("SESSION=","") if session_cookie else None

        self.client_endpoint = hyperlink.parse(client_endpoint).normalize()
        self.auth_uri = auth_uri

        self.auth_manager = auth_manager
        if not self.auth_manager:
            if token:
                logging.warning("Parameter token is deprecated, provide a contentgrid_hal_client.security.PlainAccessTokenApplicationAuthenticationManager "
                                "and use auth_manager instead.")
                self.auth_manager = PlainAccessTokenApplicationAuthenticationManager(resources=[self.client_endpoint.to_text()], access_token=token)
            elif client_id and client_secret:
                logging.warning("Parameters client_id, client_secret and auth_uri are deprecated, "
                                "provide a contentgrid_hal_client.security.ClientCredentialsApplicationAuthenticationManager and use auth_manager instead.")
                if not auth_uri:
                    raise ValueError("Auth uri is required when using a service account.")
                self.auth_manager = ClientCredentialsApplicationAuthenticationManager(resources=[self.client_endpoint.to_text()], auth_uri=auth_uri, client_id=client_id, client_secret=client_secret)
            elif session_cookie:
                assert self.session_cookie
                self.cookies.set(name="SESSION", value=self.session_cookie)
            else:
                raise ValueError("Authentication manager is required.")

        # Retries requests for status_forcelist response codes with backoff factor increasing wait time between each request
        retries = Retry(total=5,
                backoff_factor=0.2,
                status_forcelist=[ 500, 502, 503, 504 ])

        self.mount('http://', HTTPAdapter(max_retries=retries, pool_maxsize=pool_maxsize))
        self.mount('https://', HTTPAdapter(max_retries=retries, pool_maxsize=pool_maxsize))

        logging.info(f"ContentGrid deployment endpoint: {self.client_endpoint.to_text()}")
        self.headers["Accept"] = "application/prs.hal-forms+json"
        logging.info(f"Client Cookies : {self.cookies.items()}")

    def _transform_hal_links_to_uris(self, attributes : dict) -> None:
        for attribute, value in attributes.items():
            if isinstance(value, list):
                for i, v in enumerate(value):
                    if isinstance(v, HALLink):
                        attributes[attribute][i] = v.uri
            else:
                if isinstance(value, HALLink):
                    attributes[attribute] = value.uri

    def _create_text_uri_list_payload(self, links : List[str | HALLink | HALResponse]) -> str:
        uri_list = []
        for link in links:
            if isinstance(link, HALLink):
                uri_list.append(link.uri)
            elif isinstance(link, HALResponse):
                uri_list.append(link.get_self_link().uri)
            elif isinstance(link, str):
                uri_list.append(link)
            else:
                raise BadRequest(f"Incorrect Link type {type(link)} in uri list payload, allowed types: HALLink, HALResponse or str")
        return "\n".join(uri_list)

    def _validate_non_json_response(self, response: requests.Response) -> requests.Response:
        self._raise_for_status(response)
        return response

    def _validate_json_response(self, response: requests.Response) -> dict:
        self._raise_for_status(response)
        if response.status_code < 300:
            try:
                return response.json()
            except JSONDecodeError as e:
                logging.error(f"Failed to parse JSON, error: {str(e)}")
                return response.content # type: ignore
        else:
            raise requests.HTTPError(f"Unexpected response status {response.status_code} code was not caught.")

    def _raise_for_status(self, response: requests.Response):
        """Raises :class:`HTTPError`, if one occurred."""

        http_error_msg = ""
        if hasattr(response, "reason") and isinstance(response.reason, bytes):
            # We attempt to decode utf-8 first because some servers
            # choose to localize their reason strings. If the string
            # isn't utf-8, we fall back to iso-8859-1 for all other
            # encodings. (See PR #3538)
            try:
                reason = response.reason.decode("utf-8")
            except UnicodeDecodeError:
                reason = response.reason.decode("iso-8859-1")
        else:
            if hasattr(response, "reason"):
                reason = response.reason
            else:
                reason = "reason unknown"

        if 400 <= response.status_code < 500:
            http_error_msg = (
                f"{response.status_code} Client Error: {reason} for url: {response.url}. response: {response.text}"
            )

        elif 500 <= response.status_code < 600:
            http_error_msg = (
                f"{response.status_code} Server Error: {reason} for url: {response.url}. response: {response.text}"
            )

        if http_error_msg:
            raise requests.HTTPError(http_error_msg, response=response)


    def _add_page_and_size_to_params(self, size , params):
        # Check if params does not contain page or size, if not set it to page and size (or defaults)
        # params dict has precendence over page and size variables
        if "_size" not in params.keys():
            params["_size"] = size
        return params

    def request(self, method, url, *args, **kwargs) -> requests.Response:
        abs_url = self.client_endpoint.click(url).normalize().to_text()
        logging.debug(f"{method} - {abs_url}")
        if "params" in kwargs:
            logging.debug(f"params: {kwargs['params']}")
        if "json" in kwargs:
            logging.debug(f"Json payload: {json.dumps(kwargs['json'], indent=4)}")
        if self.auth_manager:
            # Automatically refreshes token if expired
            self.headers["Authorization"] = (
                f"Bearer {self.auth_manager.for_url(abs_url).access_token}"
            )
        response = super().request(
            method, abs_url, *args, **kwargs
        )
        if self.auth_manager and "www-authenticate" in response.headers.keys():
            error = parse_authenticate_error(response)
            auth_manager = self.auth_manager.for_url(abs_url)
            logging.debug(f"Authorization error - Status code: {response.status_code}, error: {error}")

            if response.status_code == 401 and error.get("error", None) == "invalid_token":
                logging.warning("Contentgrid authorization token no longer valid.")
                logging.debug("Refreshing token...")
                auth_manager.refresh()  # Manual refresh, overriding cache

                self.headers["Authorization"] = (
                    f"Bearer {auth_manager.access_token}"
                )
                response = super().request(
                    method, abs_url, *args, **kwargs
                )
            elif response.status_code == 403 and error.get("error", None) == "insufficient_scope":
                logging.warning("Contentgrid authorization token has insufficient scope.")
                missing_scope = error.get("scope", None)
                if missing_scope:
                    logging.debug(f"Adding missing scope '{missing_scope}' to existing scope '{auth_manager.scope_hint or ''}'")
                    auth_manager.extend_scope(missing_scope)

                    self.headers["Authorization"] = (
                        f"Bearer {auth_manager.access_token}"
                    )
                    response = super().request(
                        method, abs_url, *args, **kwargs
                    )
        return response
    
    T = TypeVar('T', bound=HALResponse)  
    def follow_link(self, link: Optional["HALLink"], infer_type: Type[T]=HALResponse, params={}) -> T: #type: ignore
        assert link is not None
        response = self.get(link.uri, params=params) # type: ignore
        data = self._validate_json_response(response=response)
        if isinstance(data, dict):
            if issubclass(infer_type, InteractiveHALResponse): 
                return infer_type(data=data, client=self) # type: ignore
            return infer_type(data=data)
        else:
            raise Exception("Followed link did not provide json data. Use follow_link_non_json for non json data")
            return
        
    def follow_link_non_json(self, link : Optional["HALLink"], params={}) -> bytes:
        assert link is not None
        response = self.get(link.uri, params=params) # type: ignore
        self._validate_non_json_response(response=response)
        return response.content

    def get_method_from_string(self, http_method:str):
        method_dict = {
            "GET" : self.get,
            "POST" : self.post,
            "PATCH" : self.patch,
            "DELETE" : self.delete,
            "PUT" : self.put
        }
        if http_method not in method_dict.keys():
            raise Exception(f"Unkown method from HAL-forms: {http_method}")
        return method_dict[http_method]