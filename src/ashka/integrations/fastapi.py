from importlib.util import find_spec

from dishka import AsyncContainer, Container

from ._dispatch import dishka_setup, get_container_

if find_spec("fastapi"):
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

    def setup_dishka(
        container: Container | AsyncContainer,
        app: FastAPI,
        *args: object,
        **kwargs: object,
    ):
        _dishka_setup(app, container, *args, **kwargs)

    @get_container_.register(FastAPI)
    def get_container(app: FastAPI) -> Container | AsyncContainer:
        return app.state.dishka_container
