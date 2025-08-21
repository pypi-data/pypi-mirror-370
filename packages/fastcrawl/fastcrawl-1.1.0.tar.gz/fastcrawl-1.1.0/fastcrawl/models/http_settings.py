from typing import Optional, Union

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict

from fastcrawl import types_


class HttpSettings(BaseSettings):
    """Settings for HTTP client.

    Attributes:
        base_url (Union[httpx.URL, str]): The base URL for HTTP requests. Defaults to an empty string.
        auth (Optional[types_.Auth]): Auth to use for HTTP requests. Defaults to None.
        query_params (Optional[types_.QueryParams]): Query parameters to include in HTTP requests. Defaults to None.
        headers (Optional[types_.Headers]): Headers to include in HTTP requests. Defaults to None.
        cookies (Optional[types_.Cookies]): Cookies to include in HTTP requests. Defaults to None.
        verify (bool): Whether to verify SSL certificates. Defaults to True.
        http1 (bool): Whether to use HTTP/1.1. Defaults to True.
        http2 (bool): Whether to use HTTP/2. Defaults to False.
        proxy (Optional[Union[httpx.URL, str]]): Proxy URL to use for HTTP requests. Defaults to None.
        timeout (float): Timeout for HTTP requests in seconds. Defaults to 5 seconds.
        max_connections (Optional[int]): Maximum number of connections to allow. Defaults to 100.
        max_keepalive_connections (Optional[int]): Maximum number of keep-alive connections. Defaults to 20.
        keepalive_expiry (Optional[float]): Time in seconds before a keep-alive connection expires. Defaults to 5 seconds.
        follow_redirects (bool): Whether to follow redirects. Defaults to False.
        max_redirects (int): Maximum number of redirects to follow. Defaults to 20.
        default_encoding (str): Default encoding for HTTP responses. Defaults to "utf-8".

    """

    base_url: Union[httpx.URL, str] = ""
    auth: Optional[types_.Auth] = None
    query_params: Optional[types_.QueryParams] = None
    headers: Optional[types_.Headers] = None
    cookies: Optional[types_.Cookies] = None
    verify: bool = True
    http1: bool = True
    http2: bool = False
    proxy: Optional[Union[httpx.URL, str]] = None
    timeout: float = 5.0
    max_connections: Optional[int] = 100
    max_keepalive_connections: Optional[int] = 20
    keepalive_expiry: Optional[float] = 5.0
    follow_redirects: bool = False
    max_redirects: int = 20
    default_encoding: str = "utf-8"

    model_config = SettingsConfigDict(
        arbitrary_types_allowed=True,
        env_prefix="fastcrawl_http_",
        extra="ignore",
    )
