from asyncio import gather
from typing import Any

from ashka.entities.bootstrap import (
    bootstrap_keys_by_container,
    bootstrap_sources,  # pyright: ignore[reportUnknownVariableType]
)

import dishka
from dishka.provider import BaseProvider

__all__ = ["make_async_container"]

_make_async_container = dishka.make_async_container

_aenter = dishka.AsyncContainer.__aenter__


async def __aenter__(self: dishka.AsyncContainer):
    aenter = await _aenter(self)

    if self in bootstrap_keys_by_container:
        await gather(
            *(
                self.get(key.type_hint, key.component)
                for key in bootstrap_keys_by_container[self]
            )
        )

    return aenter


dishka.AsyncContainer.__aenter__ = __aenter__


async def init(self: dishka.AsyncContainer):
    await self.__aenter__()


dishka.AsyncContainer.init = init  # pyright: ignore[reportAttributeAccessIssue]


def make_async_container(
    *providers: BaseProvider, **kwargs: Any
) -> dishka.AsyncContainer:
    bootstrap_keys_by_container[
        async_container := _make_async_container(*providers, **kwargs)
    ] = [
        factory.provides.with_component(provider.component)
        for provider in providers
        for factory in provider.factories
        if getattr(factory.source, "__func__", factory.source) in bootstrap_sources
    ]

    return async_container


dishka.make_async_container = dishka.async_container.make_async_container = (
    make_async_container
)
