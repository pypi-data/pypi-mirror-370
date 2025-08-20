import asyncio
from typing import TypeVar, Awaitable, cast

T = TypeVar('T')

async def as_awaitable(maybe_coroutine: T | Awaitable[T]) -> T:
    if asyncio.iscoroutine(maybe_coroutine):
        return await maybe_coroutine
    return cast(T, maybe_coroutine)

type MaybeAwaitable[T] = T | Awaitable[T]
