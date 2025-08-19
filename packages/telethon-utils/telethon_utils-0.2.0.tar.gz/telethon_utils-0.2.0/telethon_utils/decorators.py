import asyncio
from typing import Callable, Coroutine, Optional, ParamSpec, TypeVar

from telethon.errors import FloodWaitError  # type: ignore

P = ParamSpec("P")
T = TypeVar("T")


def auto_wait_flood_wait_error(
    f: Optional[Callable[P, Coroutine[None, None, T]]] = None, max_retries: int = 5
) -> Callable[P, Coroutine[None, None, T]]:
    """Decorator to auto wait on FloodWaitError."""

    assert f, "No function was passed!"

    class Data:
        retries_count = 0
        max_tries = max_retries

    async def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await f(*args, **kwargs)

        except FloodWaitError as e:
            if Data.retries_count > max_retries:
                raise e
            Data.retries_count += 1
            print(
                f"Waiting for {e.seconds} seconds on FloodWaitError ... Try: {Data.retries_count}"
            )
            await asyncio.sleep(e.seconds + 1)
            return await inner(*args, **kwargs)

    return inner
