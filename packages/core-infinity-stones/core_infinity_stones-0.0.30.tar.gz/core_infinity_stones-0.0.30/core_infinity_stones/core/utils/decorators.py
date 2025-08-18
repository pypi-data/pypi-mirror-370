import time
import functools
import asyncio

from typing import Awaitable, Callable, Type, Tuple, TypeVar, ParamSpec, cast

T = TypeVar("T")
P = ParamSpec("P")


def retry(
    max_attempts: int = 3,
    delay_in_seconds: float = 1.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    A retry decorator that works with both sync and async functions,
    and preserves type annotations.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await cast(Callable[P, Awaitable[T]], func)(
                            *args, **kwargs
                        )
                    except exceptions:
                        if attempt == max_attempts:
                            raise
                        await asyncio.sleep(delay_in_seconds)
                raise RuntimeError(
                    f"Function {func.__name__} failed after {max_attempts} attempts"
                )

            return cast(Callable[P, T], async_wrapper)

        else:

            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions:
                        if attempt == max_attempts:
                            raise
                        time.sleep(delay_in_seconds)
                raise RuntimeError(
                    f"Function {func.__name__} failed after {max_attempts} attempts"
                )

            return sync_wrapper

    return decorator
