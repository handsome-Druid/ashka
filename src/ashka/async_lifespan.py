from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import cast

from ashka.async_container import AsyncContainerType
from ashka.integrations import get_container


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
            await get_container(app).init()
            try:
                yield
            finally:
                await get_container(app).close()


    """
    await cast(AsyncContainerType, get_container(app)).init()
    try:
        yield
    finally:
        await cast(AsyncContainerType, get_container(app)).close()
