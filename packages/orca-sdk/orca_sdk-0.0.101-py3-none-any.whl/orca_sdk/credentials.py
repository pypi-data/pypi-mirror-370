from datetime import datetime
from typing import Literal, NamedTuple

import httpx
from httpx import ConnectError, Headers

from .client import orca_api

Scope = Literal["ADMINISTER", "PREDICT"]
"""
The scopes of an API key.

- `ADMINISTER`: Can do anything, including creating and deleting organizations, models, and API keys.
- `PREDICT`: Can only call model.predict and perform CRUD operations on predictions.
"""


class ApiKeyInfo(NamedTuple):
    """
    Named tuple containing information about an API key

    Attributes:
        name: Unique name of the API key
        created_at: When the API key was created
    """

    name: str
    created_at: datetime
    scopes: set[Scope]


class OrcaCredentials:
    """
    Class for managing Orca API credentials
    """

    @staticmethod
    def get_api_url() -> str:
        """
        Get the Orca API base URL that is currently being used
        """
        return str(orca_api.base_url)

    @staticmethod
    def list_api_keys() -> list[ApiKeyInfo]:
        """
        List all API keys that have been created for your org

        Returns:
            A list of named tuples, with the name and creation date time of the API key
        """
        return [
            ApiKeyInfo(
                name=api_key["name"],
                created_at=datetime.fromisoformat(api_key["created_at"]),
                scopes=set(api_key["scope"]),
            )
            for api_key in orca_api.GET("/auth/api_key")
        ]

    @staticmethod
    def is_authenticated() -> bool:
        """
        Check if you are authenticated to interact with the Orca API

        Returns:
            True if you are authenticated, False otherwise
        """
        try:
            return orca_api.GET("/auth")
        except ValueError as e:
            if "Invalid API key" in str(e):
                return False
            raise e

    @staticmethod
    def create_api_key(name: str, scopes: set[Scope] = {"ADMINISTER"}) -> str:
        """
        Create a new API key with the given name and scopes

        Params:
            name: The name of the API key
            scopes: The scopes of the API key

        Returns:
            The secret value of the API key. Make sure to save this value as it will not be shown again.
        """
        res = orca_api.POST(
            "/auth/api_key",
            json={"name": name, "scope": list(scopes)},
        )
        return res["api_key"]

    @staticmethod
    def revoke_api_key(name: str) -> None:
        """
        Delete an API key

        Params:
            name: The name of the API key to delete

        Raises:
            ValueError: if the API key is not found
        """
        orca_api.DELETE("/auth/api_key/{name_or_id}", params={"name_or_id": name})

    @staticmethod
    def set_headers(headers: dict[str, str]):
        """
        Add or override default HTTP headers for all Orca API requests.

        Args:
            **kwargs: Header names with their string values

        Notes:
            New keys are merged into the existing headers, this will overwrite headers with the
            same name, but leave other headers untouched.
        """
        orca_api.headers.update(Headers(headers))

    @staticmethod
    def set_api_key(api_key: str, check_validity: bool = True):
        """
        Set the API key to use for authenticating with the Orca API

        Note:
            The API key can also be provided by setting the `ORCA_API_KEY` environment variable

        Params:
            api_key: The API key to set
            check_validity: Whether to check if the API key is valid and raise an error otherwise

        Raises:
            ValueError: if the API key is invalid and `check_validity` is True
        """
        OrcaCredentials.set_headers({"Api-Key": api_key})
        if check_validity:
            orca_api.GET("/auth")

    @staticmethod
    def set_base_url(base_url: str, check_validity: bool = True):
        """
        Set the base URL for the Orca API

        Args:
            base_url: The base URL to set
            check_validity: Whether to check if there is an API running at the given base URL

        Raises:
            ValueError: if there is no healthy API running at the given base URL and `check_validity` is True
        """
        # check if the base url is reachable before setting it
        if check_validity:
            try:
                httpx.get(base_url, timeout=1)
            except ConnectError as e:
                raise ValueError(f"No API found at {base_url}") from e

        orca_api.base_url = base_url

        # check if the api passes the health check
        if check_validity:
            orca_api.GET("/")

    @staticmethod
    def is_healthy() -> bool:
        """
        Check whether the API is healthy

        Returns:
            True if the API is healthy, False otherwise
        """
        try:
            orca_api.GET("/")
            orca_api.GET("/gpu/")
        except Exception:
            return False
        return True
