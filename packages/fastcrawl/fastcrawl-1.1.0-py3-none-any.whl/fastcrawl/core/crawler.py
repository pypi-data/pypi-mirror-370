import copy
import logging
from typing import Callable, Dict, List, Optional

import pydantic

from fastcrawl import models
from fastcrawl.core import components, http_client


class Crawler:
    """FastCrawl crawler.

    Crawler must be included in the FastCrawl application.
    Several crawlers in one application can be used to crawl different websites
    or different parts of the same website.

    Args:
        name (str): Name of the crawler.
        http_settings (Optional[models.HttpSettings]): HTTP settings for the crawler.
            Note that the crawler HTTP settings are merged with the application HTTP settings.
            Application HTTP settings are considered as a base for the crawler HTTP settings.
            Provided HTTP settings will override the application HTTP settings for the crawler.
            If not provided, default HTTP settings will be used. Defaults to None.

    """

    name: str
    logger: logging.Logger

    _http_client: http_client.HTTPClient
    _startup: Optional[components.Startup]
    _handlers: Dict[Callable, components.Handler]
    _pipelines: List[components.Pipeline]
    _start_requests: List[models.Request]

    def __init__(self, name: str, http_settings: Optional[models.HttpSettings] = None) -> None:
        self.name = name
        self.logger = logging.getLogger(name)
        self._http_client = http_client.HTTPClient(http_settings or models.HttpSettings())

        self._startup = None
        self._handlers = {}
        self._pipelines = []
        self._start_requests = []

    def startup(self) -> Callable:
        """Function that is called once before the crawler is started.

        Can be used to initialize custom start requests or any other setups.

        Requirements:
            - Only one startup function can be defined for each crawler.
            - Must have type annotations for its dependencies and return value.
            - Can return or yield request(s).
            - Requests must be instances of `fastcrawl.Request`.

        Raises:
            ValueError: If a startup function is already defined.

        """

        def decorator(func: Callable) -> Callable:
            if self._startup is not None:
                raise ValueError("Only one startup function can be defined for each crawler.")
            self._startup = components.Startup(func)
            return func

        return decorator

    def handler(self, *urls: str) -> Callable:
        """Handler that processes HTTP responses.

        Requirements:
            - Must have type annotations for its arguments, dependencies and return value.
            - Must have a response argument of type `fastcrawl.Response` (with any name).
            - Can return or yield item(s) or new request(s).
            - Items must be instances of pydantic models.
            - Requests must be instances of `fastcrawl.Request`.

        Args:
            urls (str): URLs to handle. Can be a single string or multiple strings.
                If provided, URLs will be used to create initial requests
                and will be processed by the handler.

        Raises:
            TypeError: If any URL is not a string.

        """

        def decorator(func: Callable) -> Callable:
            self._handlers[func] = components.Handler(func)
            for url in urls:
                if not isinstance(url, str):
                    raise TypeError(f"URL must be a string, got {type(url)}")
                self._start_requests.append(models.Request(url=url, handler=func))
            return func

        return decorator

    def pipeline(self, priority: Optional[int] = None) -> Callable:
        """Pipeline that processes items.

        Requirements:
            - Must have type annotations for its arguments, dependencies and return value.
            - Must have an item argument which is a pydantic model (with any name).
                The model you specify will be the expected item type for the pipeline.
                If pipeline got an item not of the expected type, item processing will be skipped.
            - Can return processed item or None if no further processing is needed.

        Args:
            priority (Optional[int]): Priority of the pipeline.
                Must be a non-negative integer. If not provided, the pipeline
                will be added to the end of the list. Defaults to None.

        Raises:
            TypeError: If priority is not a non-negative integer.

        """

        def decorator(func: Callable) -> Callable:
            if priority is not None and (not isinstance(priority, int) or priority < 0):
                raise TypeError("Priority must be a non-negative integer.")

            pipeline = components.Pipeline(func)
            if priority is None:
                self._pipelines.append(pipeline)
            else:
                self._pipelines.insert(priority, pipeline)

            return func

        return decorator

    async def _process_request(self, request: models.Request) -> Optional[models.Response]:
        response = await self._http_client.request(request)
        if response:
            self.logger.debug("Got response: %s", response)
        else:
            self.logger.debug("Request already processed, skipping: %s", request)
        return response

    async def _process_response(self, response: models.Response) -> components.HandlerReturnType:
        handler = self._handlers[response.request.handler]
        async for value in handler.execute(response):
            if value is not None:
                yield value

    async def _process_item(self, item: pydantic.BaseModel) -> None:
        processed_item: Optional[pydantic.BaseModel] = copy.deepcopy(item)
        for pipeline in self._pipelines:
            if not processed_item or not pipeline.is_compatible_item(processed_item):
                continue
            processed_item = await pipeline.execute(processed_item)
            if not processed_item:
                break
