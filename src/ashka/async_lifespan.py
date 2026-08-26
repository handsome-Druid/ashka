from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import getLogger

from ashka.integrations import get_container

from dishka import AsyncContainer, Container

_logger = getLogger(__name__)


@asynccontextmanager
async def async_lifespan(app: object) -> AsyncGenerator[None, None]:
    """
    Manage the application container lifecycle.

    Only available when installed with `ashka[lifecycle]`.

    Examples
    --------
    If you need a custom lifespan, copy the entire implementation into your code and modify it there instead of importing `async_lifespan` from this repository and trying to patch it::

        @asynccontextmanager
        async def async_lifespan(app: object) ->  AsyncGenerator[None, None]:
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
