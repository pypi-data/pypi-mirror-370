import logging
from typing import Any, Callable, Optional, TypeVar
from uuid import uuid4
import redis.asyncio as redis

T = TypeVar("T")
U = TypeVar("U")

logger = logging.Logger(__name__)


class RedisClient:
    def __init__(self, client: redis.Redis):
        self.redis_client = client


    async def set_value(
        self,
        key: T,
        value: U,
        key_encoder: Optional[Callable[[Any], str]] = None,
        value_encoder: Optional[Callable[[Any], str]] = None,
        expiration_time: Optional[int] = None
    ) -> None:
        await self.set_values(
            keys_by_values={key: value},
            key_encoder=key_encoder,
            value_encoder=value_encoder,
            expiration_time=expiration_time
        )


    async def set_values(
        self,
        keys_by_values: dict[T, U],
        key_encoder: Optional[Callable[[Any], str]] = None,
        value_encoder: Optional[Callable[[Any], str]] = None,
        expiration_time: Optional[int] = None
    ) -> None:
        pipeline = self.redis_client.pipeline()

        for key, value in keys_by_values.items():
            if value is None:
                continue

            string_key = self._encode_key_as_string(key, key_encoder)
            string_value = self._encode_value_as_string(value, value_encoder)

            pipeline.set(string_key, string_value, ex=expiration_time)

        await pipeline.execute()


    async def get_value(
        self,
        key: str
    ) -> Optional[str]:
        result = await self.redis_client.get(key)
        return result


    async def _get_values(
        self,
        keys: list[str]
    ) -> list[Optional[str]]:
        results = await self.redis_client.mget(keys)
        return results


    async def get_values_dict(
        self,
        keys: list[str]
    ) -> dict[str, Optional[str]]:
        results = await self._get_values(keys)
        return self._create_dictionary(keys, results)


    async def get_decoded_value(
        self,
        key: U,
        value_decoder: Callable[[str], T],
        key_encoder: Optional[Callable[[Any], str]] = None,
    ) -> Optional[T]:
        decoded_values = await self._get_decoded_values([key], value_decoder, key_encoder)

        if not decoded_values:
            return None

        return decoded_values[0]


    async def _get_decoded_values(
        self,
        keys: list[T],
        value_decoder: Callable[[str], U],
        key_encoder: Optional[Callable[[Any], str]] = None,
    ) -> list[Optional[U]]:
        string_keys = [self._encode_key_as_string(key, key_encoder) or str(uuid4()) for key in keys]

        results = await self.redis_client.mget(string_keys)

        decoded_results: list[Optional[U]] = []

        for result in results:
            if result is None:
                decoded_results.append(None)
                continue

            decoded_result = self._decode_value(result, value_decoder)
            decoded_results.append(decoded_result)

        return decoded_results


    async def get_decoded_values_dict(
        self,
        keys: list[T],
        value_decoder: Callable[[str], U],
        key_encoder: Optional[Callable[[T], str]] = None,
    ) -> dict[T, Optional[U]]:
        """Returns The values from cache as a dictionary whose keys are the original unencoded keys."""
        values = await self._get_decoded_values(keys, value_decoder, key_encoder)
        return self._create_dictionary(keys, values)


    async def delete(self, key: T, key_encoder: Optional[Callable[[T], str]] = None) -> None:
        string_key = self._encode_key_as_string(key, key_encoder)

        self.redis_client.delete(string_key)


    async def clear_all_values(self) -> None:
        self.redis_client.flushdb()

    # MARK: Convenience Methods

    def _get_as_string(
        self, 
        value: Any,
        encoder: Optional[Callable[[Any], str]],
        no_encoder_error_message: str,
        invalid_encoder_return_type_error: str,
    ) -> str:
        if isinstance(value, str):
            return value

        if isinstance(value, int) or isinstance(value, float):
            return str(value)

        if encoder is None:
            raise ValueError(no_encoder_error_message)

        try:
            string_value = encoder(value)
        except Exception as e:
            logger.error(f"Error encoding value: {value}, error: {e}")
            raise e

        if not isinstance(string_value, str):
            raise ValueError(invalid_encoder_return_type_error)

        return string_value


    def _encode_key_as_string(self, key: Any, key_encoder: Optional[Callable[[Any], str]]) -> str:
        string_key = self._get_as_string(
            value=key,
            encoder=key_encoder,
            no_encoder_error_message=f"string key_encoder is required for non-string key: {key}",
            invalid_encoder_return_type_error=f"key encoder must return a string for key: {key}",
        )
    
        if string_key is None:
            raise ValueError(f"Error encoding key: {key}")

        return string_key


    def _encode_value_as_string(self, value: Any, value_encoder: Optional[Callable[[Any], str]]) -> str:
        return self._get_as_string(
            value=value,
            encoder=value_encoder,
            no_encoder_error_message=f"string value_encoder is required for non-string value: {value}",
            invalid_encoder_return_type_error=f"value encoder must return a string for value: {value}",
        )


    def _decode_value(self, value: str, value_decoder: Callable[[str], T]) -> T:
        try:
            decoded_result = value_decoder(value)
        except Exception as e:
            error_message = f"Redis client error decoding value: {value}, error: {e}"
            logger.error(error_message)
            raise Exception(error_message)
        return decoded_result


    def _create_dictionary(self, keys: list[Any], values: list[Any]) -> dict[Any, Any]:
        return dict(zip(keys, values))


async def create_redis_client(host: str, port: str, db: int) -> "RedisClient":
    url = f"redis://{host}:{port}/{db}"
    client = await redis.from_url(url, decode_responses=True)
    return RedisClient(client=client)