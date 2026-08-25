from collections.abc import Callable
from importlib.util import find_spec

from ashka.async_container import AsyncContainerType
from ashka.container import ContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer, Container
from dishka.integrations.fastapi import setup_dishka

if find_spec("fastapi"):
    try:
        from dishka.integrations import fastapi
        from fastapi import FastAPI

        __all__: list[str] = ["get_container", "setup_dishka"]

        @dishka_setup.register(FastAPI)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            app: FastAPI,
            container: Container | AsyncContainer,
            *args: object,
            **kwargs: object,
        ) -> None:
            fastapi.setup_dishka(container, app, *args, **kwargs)

        setup_dishka: Callable[..., None] = fastapi.setup_dishka

        @get_container_.register(FastAPI)
        def get_container(app: FastAPI) -> ContainerType | AsyncContainerType:
            return app.state.dishka_container
    except ImportError:  # pragma: no cover
        pass
