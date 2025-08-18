from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

from core_infinity_stones.networking.response_handler import HttpxResponse

T = TypeVar("T", bound=BaseModel)


class BaseModelResponseDecoder(Generic[T]):
    def __init__(self, model: type[T]):
        self.model = model

    def decode_as_object(self, response: HttpxResponse) -> T:
        return self.model(**response.json())

    def decode_as_list(self, response: HttpxResponse) -> list[T]:
        return [self.model(**element) for element in response.json()]

    def decode_as_str_to_model_map(self, response: HttpxResponse) -> dict[str, T]:
        return {key: self.model(**value) for key, value in response.json().items()}

    def decode_as_uuid_to_model_map(self, response: HttpxResponse) -> dict[UUID, T]:
        return {
            UUID(key): self.model(**value) for key, value in response.json().items()
        }
