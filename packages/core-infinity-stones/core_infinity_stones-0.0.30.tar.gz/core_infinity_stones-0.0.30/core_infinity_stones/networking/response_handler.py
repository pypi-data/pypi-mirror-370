from typing import Callable, Optional, TypeVar

from core_infinity_stones.errors.response_status_code_error import (
    ResponseStatusCodeError,
)

from .schemas import HttpxResponse

T = TypeVar("T")


class ResponseHandler:
    @staticmethod
    def handle(
        response: HttpxResponse,
        source_url: str,
        decoder: Callable[[HttpxResponse], T] = lambda response: response.text,  # type: ignore
        successful_status_codes_range: range = range(200, 300),
        error_messages_by_status_codes: Optional[dict[int, str]] = None,
    ) -> T:
        if response.status_code in successful_status_codes_range:
            return decoder(response)

        raise ResponseStatusCodeError(
            url=source_url,
            status_code=response.status_code,
            debug_description=response.text,
            messages_by_status_codes=error_messages_by_status_codes,
        )
