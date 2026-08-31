from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import getLogger

from ashka.integrations import get_container

from dishka import AsyncContainer, Container

_logger = getLogger(__name__)


@asynccontextmanager
async def async_lifespan(app: object) -> AsyncGenerator[None, None]:
    """
    Manage the async application container lifecycle.

    Not recommended to use a sync container with an async application.

    Installing `ashka[lifecycle]` automatically attaches `container.init()` to the
    lifespan.

    Examples
    --------
    If you need a custom lifespan, copy the example implementation into your code and modify it there instead of importing `async_lifespan` from this repository and trying to patch it::

        @asynccontextmanager
        async def lifespan(app: object) ->  AsyncGenerator[None, None]:
            async with get_container(app):
                yield
    """
    match container := get_container(app):
        case AsyncContainer():
            async with container:
                yield
        case Container():
            _logger.warning(
                "Should not use a sync container with async lifespan; "
                "use an async container instead."
            )
            with container:
                yield
        case _:  # pragma: nocover
            raise TypeError(f"Expected 'dishka.AsyncContainer', got {type(container)!r}")
