import json
from typing import Any, Optional

import httpx
import parsel
from pydantic import BaseModel, ConfigDict, PrivateAttr

from fastcrawl import types_
from fastcrawl.models.request import Request


class Response(BaseModel):
    """HTTP response model.

    Attributes:
        url (httpx.URL): The URL of the response.
        status_code (int): The HTTP status code of the response.
        is_success (bool): Whether the request was successful (status code 200-299).
        content (bytes): The raw content of the response.
        text (str): The text content of the response.
        headers (Optional[types_.Headers]): The headers of the response. Defaults to None.
        cookies (Optional[types_.Cookies]): The cookies of the response. Defaults to None.
        request (Request): The request that generated this response.

    """

    url: httpx.URL
    status_code: int
    is_success: bool
    content: bytes
    text: str
    headers: Optional[types_.Headers] = None
    cookies: Optional[types_.Cookies] = None
    request: Request
    _cached_selector: Optional[parsel.Selector] = PrivateAttr(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    async def from_httpx_response(cls, httpx_response: httpx.Response, request: Request) -> "Response":
        """Returns a Response instance from an `httpx.Response` instance.

        Args:
            httpx_response (httpx.Response): Instance of `httpx.Response` to convert.
            request (Request): The request that generated this response.

        """
        try:
            content = httpx_response.content
        except httpx.ResponseNotRead:
            content = await httpx_response.aread()

        return cls(
            url=httpx_response.url,
            status_code=httpx_response.status_code,
            is_success=httpx_response.is_success,
            content=content,
            text=httpx_response.text,
            headers=dict(httpx_response.headers),
            cookies=dict(httpx_response.cookies),
            request=request,
        )

    def get_json_data(self) -> Any:
        """Returns the JSON data from the response content."""
        return json.loads(self.text)

    @property
    def selector(self) -> parsel.Selector:
        """Selector for parsing the response content."""
        if self._cached_selector is None:
            self._cached_selector = parsel.Selector(text=self.text)
        return self._cached_selector

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}({self.status_code}, {self.url})>"
