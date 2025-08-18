from typing import Any, Callable, Protocol


class HttpxResponse(Protocol):
    status_code: int
    json: Callable[[], Any]
    text: str
