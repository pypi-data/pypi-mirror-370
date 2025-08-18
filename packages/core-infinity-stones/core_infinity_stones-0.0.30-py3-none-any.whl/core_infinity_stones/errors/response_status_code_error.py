from typing import Optional
from core_infinity_stones.errors.base_error import BaseError


class ResponseStatusCodeError(BaseError):
    def __init__(
        self,
        url: str,
        status_code: int,
        debug_description: str,
        messages_by_status_codes: Optional[dict[int, str]] = None,
    ):
        error_message = (
            messages_by_status_codes.get(status_code)
            if messages_by_status_codes
            else None
        )

        super().__init__(
            status_code=status_code,
            occurred_while=f"calling {url}",
            debug_description=debug_description,
            message=error_message,
        )

    @property
    def message(self) -> str:
        if self._message:
            return self._message
        return "Something went wrong"
