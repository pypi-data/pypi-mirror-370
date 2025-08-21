import json
import logging
from typing import Any, Optional

import httpx

from fastcrawl import models


class HTTPClient:
    """Client for making HTTP requests.

    This class manages HTTP settings and provides methods to make requests using the httpx library.

    Args:
        http_settings (models.HttpSettings): Configuration settings for the HTTP client.

    """

    logger: logging.Logger

    _http_settings: models.HttpSettings
    _cached_httpx_client: Optional[httpx.AsyncClient]
    _processed_requests: set[int]

    def __init__(self, http_settings: models.HttpSettings) -> None:
        self._http_settings = http_settings
        self._cached_httpx_client = None
        self._processed_requests = set()

    @property
    def _httpx_client(self) -> httpx.AsyncClient:
        if not self._cached_httpx_client:
            kwargs = self._http_settings.model_dump()
            kwargs["params"] = kwargs.pop("query_params")
            kwargs["trust_env"] = False
            kwargs["limits"] = httpx.Limits(
                max_connections=kwargs.pop("max_connections"),
                max_keepalive_connections=kwargs.pop("max_keepalive_connections"),
                keepalive_expiry=kwargs.pop("keepalive_expiry"),
            )
            self._cached_httpx_client = httpx.AsyncClient(**kwargs)
        return self._cached_httpx_client

    def merge_http_clients(self, parent_http_client: "HTTPClient") -> None:
        """Merges HTTP settings from another HTTPClient instance.

        Args:
            parent_http_client (HTTPClient): The HTTPClient instance whose settings will be merged.

        """
        self._http_settings = parent_http_client._http_settings.model_copy(
            update=self._http_settings.model_dump(exclude_unset=True)
        )

    async def request(self, request: models.Request) -> Optional[models.Response]:
        """Makes an HTTP request.

        Args:
            request (models.Request): The request to be made.

        Returns:
            Optional[models.Response]: The response from the request, or None if the request has already been processed.

        """
        request_hash = self._get_request_hash(request)
        if request_hash in self._processed_requests:
            return None
        self._processed_requests.add(request_hash)

        request_kwargs = request.model_dump(exclude_none=True, exclude={"handler", "handler_data"})
        if "query_params" in request_kwargs:
            request_kwargs["params"] = request_kwargs.pop("query_params")
        if "form_data" in request_kwargs:
            request_kwargs["data"] = request_kwargs.pop("form_data")
        if "json_data" in request_kwargs:
            request_kwargs["json"] = request_kwargs.pop("json_data")
        httpx_response = await self._httpx_client.request(**request_kwargs)
        return await models.Response.from_httpx_response(httpx_response, request)

    async def close(self) -> None:
        """Closes the HTTP client and releases resources."""
        if self._cached_httpx_client and not self._cached_httpx_client.is_closed:
            await self._cached_httpx_client.aclose()
            self._cached_httpx_client = None

    def _get_request_hash(self, request: models.Request) -> int:
        data = request.model_dump(exclude={"handler"}, exclude_unset=True)
        hashable = tuple((key, self._make_value_hashable(value)) for key, value in data.items())
        return hash(hashable)

    def _make_value_hashable(self, value: Any) -> Any:
        """Returns a hashable representation of the value.

        Args:
            value (Any): The value to convert.

        """
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        try:
            return json.dumps(value, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError):
            return str(value)
