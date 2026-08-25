from asyncio import gather
from typing import Any, cast

import dishka
from dishka import AsyncContainer, DependencyKey
from dishka.provider import BaseProvider

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_keys_by_container,
    bootstrap_sources,  # pyright: ignore[reportUnknownVariableType]
)

__all__ = ["make_async_container"]

_aenter = AsyncContainer.__aenter__


async def __aenter__(self: AsyncContainer):
    aenter = await _aenter(self)

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

_make_async_container = dishka.make_async_container


def make_async_container(*providers: BaseProvider, **kwargs: Any) -> AsyncContainerType:
    container_key: set[DependencyKey] = set()

    for provider in providers:
        for factory in provider.factories:
            if (
                source := getattr(factory.source, "__func__", factory.source)
                in bootstrap_sources
            ):
                if (
                    key := factory.provides.with_component(provider.component)
                ) in container_key:
                    raise ValueError(
                        f"{source} with component: {key.component} and type hint: {key.type_hint} conflicts with other factories."
                    )
                container_key.add(key)

    bootstrap_keys_by_container[
        async_container := _make_async_container(*providers, **kwargs)
    ] = container_key
    return cast(AsyncContainerType, async_container)


dishka.make_async_container = dishka.async_container.make_async_container = (
    make_async_container
)
