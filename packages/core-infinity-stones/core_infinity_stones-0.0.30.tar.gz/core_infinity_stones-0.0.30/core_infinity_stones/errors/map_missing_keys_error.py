from typing import Any, TypeVar
from core_infinity_stones.errors.base_error import BaseError

T = TypeVar("T")


class MapIsMissingKeysError(BaseError):
    def __init__(
        self,
        status_code: int,
        occurred_while: str,
        map_name: str,
        map: dict[T, Any],
        missing_keys: list[T],
    ):
        debug_description = f"""The following keys are missing from the {map_name}
        missing_keys: {missing_keys}
        map: {map}
        """

        super().__init__(
            status_code=status_code,
            occurred_while=occurred_while,
            debug_description=debug_description,
        )
