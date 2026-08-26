from asyncio import gather
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import ParamSpec, cast

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_keys_by_container,
    bootstrap_sources,  # pyright: ignore[reportUnknownVariableType]
)

import dishka
from dishka import AsyncContainer
from dishka.provider import BaseProvider
from typing_extensions import Never

__all__: list[str] = ["make_async_container"]

_aenter: Callable[..., Coroutine[Never, object, AsyncContainer]] = (
    AsyncContainer.__aenter__
)


async def __aenter__(self: AsyncContainer) -> AsyncContainer:
    aenter: AsyncContainer = await _aenter(self)

    if self in bootstrap_keys_by_container:
        await gather(
            *(
                self.get(key.type_hint, key.component)
                for key in bootstrap_keys_by_container[self]
            )
        )

    return aenter


class AsyncContainerType(AsyncContainer):
    __slots__ = ()

    __aenter__ = __aenter__

    async def init(self) -> None:
        await self.__aenter__()


AsyncContainer.__aenter__ = __aenter__
AsyncContainer.init = AsyncContainerType.init  # pyright: ignore[reportAttributeAccessIssue]

_make_async_container: Callable[..., AsyncContainer] = dishka.make_async_container

P = ParamSpec("P")


def make_async_container_(
    make_async_container: Callable[P, AsyncContainer],
) -> Callable[..., AsyncContainerType]:
    @wraps(make_async_container)
    def inner(*providers: P.args, **kwargs: P.kwargs) -> AsyncContainerType:
        bootstrap_keys_by_container[
            async_container := _make_async_container(
                *cast(tuple[BaseProvider, ...], providers), **kwargs
            )
        ] = [
            factory.provides.with_component(provider.component)
            for provider in cast(tuple[BaseProvider, ...], providers)
            for factory in provider.factories
            if getattr(factory.source, "__func__", factory.source) in bootstrap_sources
        ]

        return cast(AsyncContainerType, async_container)

    return inner


dishka.make_async_container = dishka.async_container.make_async_container = (
    make_async_container := make_async_container_(_make_async_container)
)
