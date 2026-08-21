from importlib.util import find_spec

from dishka import AsyncContainer, Container

if find_spec("fastapi"):
    from dishka.integrations import fastapi
    from fastapi import FastAPI

    __all__ = ["get_container", "setup_dishka"]

    setup_dishka = fastapi.setup_dishka

    def get_container(app: FastAPI) -> Container | AsyncContainer:
        return app.state.dishka_container
