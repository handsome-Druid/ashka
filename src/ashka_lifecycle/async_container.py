from asyncio import gather
from collections.abc import Callable, Coroutine

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_types,
)

from dishka import AsyncContainer

_aenter: Callable[..., Coroutine[None, object, AsyncContainer]] = (
    AsyncContainer.__aenter__
)


async def __aenter__(self: AsyncContainer) -> AsyncContainer:
    aenter: AsyncContainer = await _aenter(self)

    await gather(
        *(
            self.get(key.type_hint, key.component)
            for registry in iter(
                lambda state=[self.registry]: (
                    (state[0], state.__setitem__(0, state[0].child_registry))[0]  # pyright: ignore[reportCallIssue, reportArgumentType]
                    if state[0] is not None  # pyright: ignore[reportUnnecessaryComparison]
                    else None
                ),
                None,
            )
            for key in registry.factories
            if key.type_hint in bootstrap_types
        )
    )

    return aenter


async def init(self: AsyncContainer) -> None:
    await self.__aenter__()


AsyncContainer.__aenter__ = __aenter__
AsyncContainer.init = init  # pyright: ignore[reportAttributeAccessIssue]
