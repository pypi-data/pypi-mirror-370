from typing import Callable, Optional, Union

import httpx
from pydantic import BaseModel, ConfigDict

from fastcrawl import types_


class Request(BaseModel):
    """HTTP request model.

    Attributes:
        method (str): HTTP method (e.g., GET, POST). Defaults to "GET".
        url (Union[httpx.URL, str]): The URL for the request.
        handler (Callable): A function that will handle the response after the request is executed.
        handler_data (Optional[dict]): Data that can be accessed from the handler function.
        query_params (Optional[types_.QueryParams]): Query parameters for the request. Defaults to None.
        headers (Optional[types_.Headers]): Headers for the request. Defaults to None.
        cookies (Optional[types_.Cookies]): Cookies for the request. Defaults to None.
        form_data (Optional[types_.FormData]): Form data for the request. Defaults to None.
        json_data (Optional[types_.JsonData]): JSON data for the request. Defaults to None.
        files (Optional[types_.Files]): Files to be uploaded with the request. Defaults to None.
        auth (Optional[types_.Auth]): Authentication credentials for the request. Defaults to None.
        timeout (Optional[float]): Timeout for the request in seconds. Defaults to None.
        follow_redirects (Optional[bool]): Whether to follow redirects. Defaults to None.

    """

    method: str = "GET"
    url: Union[httpx.URL, str]
    handler: Callable
    handler_data: Optional[dict] = None
    query_params: Optional[types_.QueryParams] = None
    headers: Optional[types_.Headers] = None
    cookies: Optional[types_.Cookies] = None
    form_data: Optional[types_.FormData] = None
    json_data: Optional[types_.JsonData] = None
    files: Optional[types_.Files] = None
    auth: Optional[types_.Auth] = None
    timeout: Optional[float] = None
    follow_redirects: Optional[bool] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}({self.method}, {self.url})>"
