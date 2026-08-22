from asyncio import gather
from typing import Any, cast

from ashka.entities.bootstrap import (
    bootstrap_keys_by_container,
    bootstrap_sources,  # pyright: ignore[reportUnknownVariableType]
)

import dishka
from dishka import AsyncContainer as DishkaAsyncContainer
from dishka.provider import BaseProvider

__all__ = ["AsyncContainer", "make_async_container"]


class AsyncContainer(DishkaAsyncContainer):
    __slots__ = ()

    async def __aenter__(self):
        aenter = await super().__aenter__()

        if self in bootstrap_keys_by_container:
            await gather(
                *(
                    self.get(key.type_hint, key.component)
                    for key in bootstrap_keys_by_container[self]
                )
            )

        return aenter

    async def init(self) -> None:
        await self.__aenter__()


dishka.AsyncContainer = dishka.async_container.AsyncContainer = AsyncContainer

_make_async_container = dishka.make_async_container


def make_async_container(*providers: BaseProvider, **kwargs: Any) -> AsyncContainer:
    bootstrap_keys_by_container[
        async_container := _make_async_container(*providers, **kwargs)
    ] = [
        factory.provides.with_component(provider.component)
        for provider in providers
        for factory in provider.factories
        if getattr(factory.source, "__func__", factory.source) in bootstrap_sources
    ]

    return cast(AsyncContainer, async_container)


dishka.make_async_container = dishka.async_container.make_async_container = (
    make_async_container
)
