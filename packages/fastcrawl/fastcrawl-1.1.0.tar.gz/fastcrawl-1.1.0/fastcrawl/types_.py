"""Various types used in FastCrawl.

Attributes:
    PrimitiveData: Represents a primitive data type that can be None, str, int, float, or bool.
    QueryParams: A mapping of query parameters where keys are strings and values can be primitive data or sequences of primitive data.
    Headers: A mapping of HTTP headers where keys and values are strings.
    Cookies: A mapping of cookies where keys and values are strings.
    FormData: A mapping for form data where keys are strings and values can be any type.
    JsonData: Represents JSON data which can be of any type.
    Files: A mapping of file uploads where keys are strings and values are bytes.
    Auth: A tuple representing authentication credentials (username, password).

"""

from typing import Any, Mapping, Optional, Sequence, Union

PrimitiveData = Optional[Union[str, int, float, bool]]

QueryParams = Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]]
Headers = Mapping[str, str]
Cookies = Mapping[str, str]
FormData = Mapping[str, Any]
JsonData = Any
Files = Mapping[str, bytes]
Auth = tuple[str, str]
