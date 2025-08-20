"""This module provides a wrapper for the API."""

import logging
import os
from typing import Any, Dict

from httpx import AsyncClient, BasicAuth, Client, Response
from pydantic import BaseModel

from axmp_openapi_helper.openapi.multi_openapi_spec import AuthenticationType

logger = logging.getLogger(__name__)

_TIMEOUT = os.getenv("HTTPX_DEFAULT_TIMEOUT", 10)


class AxmpAPIWrapper:
    """AxmpAPIWrapper is a wrapper for the API."""

    def __init__(
        self,
        server: str,
        /,
        *,
        headers: dict | None = None,
        cookies: dict | None = None,
        auth_type: AuthenticationType | None = AuthenticationType.NONE,
        username: str | None = None,
        password: str | None = None,
        bearer_token: str | None = None,
        api_key_name: str | None = None,
        api_key_value: str | None = None,
        tls_verify: bool | None = False,
        timeout: int | None = _TIMEOUT,
    ):
        """Initialize the AxmpAPIWrapper.

        Args:
            server (str): The server URL
            headers (dict, optional): The headers for the API request. Defaults to None.
            cookies (dict, optional): The cookies for the API request. Defaults to None.
            auth_type (AuthenticationType, optional): The authentication type. Defaults to AuthenticationType.NONE.
            username (str, optional): The username for the API request. Defaults to None.
            password (str, optional): The password for the API request. Defaults to None.
            bearer_token (str, optional): The bearer token for the API request. Defaults to None.
            api_key_name (str, optional): The api key name for the API request. Defaults to None.
            api_key_value (str, optional): The api key value for the API request. Defaults to None.
            tls_verify (bool, optional): Whether to verify the TLS certificate. Defaults to False.
            timeout (int, optional): The timeout for the API request. Defaults to _TIMEOUT.
        """
        if not server:
            raise ValueError("Server URL is required")

        self._server = server
        self._headers = headers or {}
        self._cookies = cookies or {}
        self._auth_type = auth_type
        self._username = username
        self._password = password
        self._bearer_token = bearer_token
        self._api_key_name = api_key_name
        self._api_key_value = api_key_value
        self._tls_verify = tls_verify
        self._timeout = timeout

        self._auth = None
        self._client = None
        self._async_client = None

        if self._headers.get("Content-Type") is None:
            self._headers.update({"Content-Type": "application/json"})

        if auth_type == AuthenticationType.BASIC:
            if not username or not password:
                raise ValueError(
                    "Username and password are required for Basic authentication"
                )
            self._auth = BasicAuth(username=username, password=password)

        elif auth_type == AuthenticationType.BEARER:
            if not bearer_token:
                raise ValueError("Bearer token is required for Bearer authentication")
            if self._bearer_token is not None:
                self._headers.update({"Authorization": f"Bearer {self._bearer_token}"})

        elif auth_type == AuthenticationType.API_KEY:
            if not api_key_name or not api_key_value:
                raise ValueError(
                    "API key name and value are required for API key authentication"
                )
            self._headers.update({self._api_key_name: self._api_key_value})

    @property
    def async_client(self) -> AsyncClient:
        """Get the async client."""
        if self._async_client is None:
            self._async_client = AsyncClient(
                auth=self._auth,
                base_url=self._server,
                headers=self._headers,
                cookies=self._cookies,
                verify=self._tls_verify,
                timeout=self._timeout,
            )
        return self._async_client

    @property
    def client(self) -> Client:
        """Get the client."""
        if self._client is None:
            self._client = Client(
                auth=self._auth,
                base_url=self._server,
                headers=self._headers,
                cookies=self._cookies,
                verify=self._tls_verify,
                timeout=self._timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the async and sync clients."""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None
        if self._client is not None:
            self._client.close()
            self._client = None

    async def _get_response(self, response: Response) -> Dict[str, Any]:
        """Get response from API.

        Args:
            response (Response): Response from API

        Returns:
            Dict[str, Any]: Response data
        """
        if response.status_code == 200:
            logger.debug(f"Response: {response.json()}")

            return response.json()
        else:
            logger.warning(
                f"Failed to get response: {response.status_code} {response.text}"
            )
            return {
                "result": "failed",
                "code": response.status_code,
                "message": response.text,
            }

    async def run(
        self,
        method: str,
        path: str,
        /,
        *,
        path_params: BaseModel | None = None,
        query_params: BaseModel | None = None,
        request_body: BaseModel | None = None,
    ) -> str:
        """Run the API request asynchronously.

        Args:
            method (str): The HTTP method to use
            path (str): The path to the resource
            path_params (Any, optional): Path parameters for the tool. Defaults to None.
            query_params (Any, optional): Query parameters for the tool. Defaults to None.
            request_body (Any, optional): Request body for the tool. Defaults to None.

        Returns:
            str: Response from the API
        """
        logger.debug(f"Method: {method}, Path: {path}")
        logger.debug("-" * 100)
        logger.debug(f"Path params: {path_params}")
        logger.debug(f"Query params: {query_params}")
        logger.debug(f"Request body: {request_body}")

        if path_params is not None:
            # for path parameters
            # NOTE: exclude_none=True, mode="json" is used to exclude None values and convert to json (e.g. Enum values)
            path = path.format(**path_params.model_dump(exclude_none=True, mode="json"))

            logger.debug(f"Formatted path: {path}")

        logger.debug(
            f"Query params: {query_params.model_dump_json(exclude_none=True) if query_params else None}"
        )
        logger.debug(
            f"Request body: {request_body.model_dump_json(exclude_none=True) if request_body else None}"
        )

        # NOTE: If the request body is an array, we need to get the value for the array
        request_body_array_value = None
        if request_body:
            request_body_array_value = await self._get_request_body_value_for_array(
                request_body
            )

        response = await self.async_client.request(
            method,
            path,
            params=query_params.model_dump(exclude_none=True, mode="json")
            if query_params
            else None,
            json=request_body_array_value
            if request_body_array_value
            else request_body.model_dump(exclude_none=True, mode="json")
            if request_body
            else None,
        )

        response.raise_for_status()

        return await self._get_response(response)

    async def _get_request_body_value_for_array(
        self, request_body: BaseModel
    ) -> list[Any] | None:
        """Get request body value for array.

        Args:
            request_body (BaseModel): Request body

        Returns:
            Any: Request body value
        """
        request_body_value = None
        for i, (field_name, field_info) in enumerate(
            type(request_body).model_fields.items()
        ):
            field_value = getattr(request_body, field_name)
            if i == 0 and field_value is not None:
                if isinstance(field_value, list):
                    request_body_value = [
                        item.model_dump(exclude_none=True, mode="json")
                        if isinstance(item, BaseModel)
                        else item
                        for item in field_value
                    ]
                    break
            else:
                logger.warning(f"Request body value is not array: {field_name}")
                return None

        logger.debug(f"Request body value: {request_body_value}")

        return request_body_value
