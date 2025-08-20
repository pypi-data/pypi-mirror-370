"""Object definitions used for type hinting."""

from typing import Literal

from httpx._types import QueryParamTypes, RequestContent, RequestData, RequestFiles

__all__ = [
    'HttpMethod',
    'QueryParamTypes',
    'RequestContent',
    'RequestData',
    'RequestFiles',
]

HttpMethod = Literal["get", "post", "put", "patch", "delete"]
