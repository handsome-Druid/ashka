from collections.abc import Callable
from importlib.util import find_spec
from typing import cast

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer

if find_spec("aiohttp"):
    try:
        from aiohttp.web_app import Application
        from dishka.integrations import aiohttp

        __all__: list[str] = ["get_container", "setup_dishka"]

        @dishka_setup.register(Application)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            app: Application, container: AsyncContainer, *args: object, **kwargs: object
        ) -> None:
            aiohttp.setup_dishka(container, app, *args, **kwargs)

        setup_dishka: Callable[..., None] = aiohttp.setup_dishka

        @get_container_.register(Application)
        def get_container(app: Application) -> AsyncContainerType:
            return cast(AsyncContainerType, app[aiohttp.DISHKA_CONTAINER_KEY])
    except ImportError:  # pragma: no cover
        pass
