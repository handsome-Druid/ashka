from asyncio import gather
from collections.abc import Callable, Coroutine
from logging import getLogger

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_types,
)

from dishka import AsyncContainer, Scope


def activate(): ...


_logger = getLogger(__name__)

_aenter: Callable[..., Coroutine[None, object, AsyncContainer]] = (
    AsyncContainer.__aenter__
)


async def __aenter__(self: AsyncContainer) -> AsyncContainer:
    aenter: AsyncContainer = await _aenter(self)

    if self.scope is Scope.APP:
        _logger.debug("Initiating bootstrap factories.")
        await gather(
            *(
                self.get(key.type_hint, key.component)
                for key in self.registry.factories
                if key.type_hint in bootstrap_types
            )
        )
    else:
        _logger.debug(
            f"'<dishka_container>.scope': {self.scope!r} is not 'Scope.APP', skipping bootstrap"
        )

    return aenter


async def init(self: AsyncContainer) -> None:
    if self.scope is not Scope.APP:
        _logger.warning(
            f"'<dishka_container>.scope': {self.scope!r} is not 'Scope.APP', 'container.init()' won't do any bootstrap."
        )
    await self.__aenter__()


AsyncContainer.__aenter__ = __aenter__
AsyncContainer.init = init  # pyright: ignore[reportAttributeAccessIssue]
