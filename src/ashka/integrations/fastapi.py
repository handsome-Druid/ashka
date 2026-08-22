from importlib.util import find_spec

from dishka import AsyncContainer, Container

from ..async_container import AsyncContainerType
from ..container import ContainerType
from ._dispatch import dishka_setup, get_container_

if find_spec("fastapi"):
    try:
        from dishka.integrations import fastapi
        from fastapi import FastAPI

        __all__ = ["get_container", "setup_dishka"]

        @dishka_setup.register(FastAPI)
        def _dishka_setup(
            app: FastAPI,
            container: Container | AsyncContainer,
            *args: object,
            **kwargs: object,
        ):
            fastapi.setup_dishka(container, app, *args, **kwargs)

        setup_dishka = fastapi.setup_dishka

        @get_container_.register(FastAPI)
        def get_container(app: FastAPI) -> ContainerType | AsyncContainerType:
            return app.state.dishka_container
    except ImportError:  # pragma: no cover
        pass
