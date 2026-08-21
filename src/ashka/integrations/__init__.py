from importlib import import_module

from dishka import AsyncContainer, Container

from . import fastapi, flask, sanic

__all__ = ["fastapi", "flask", "get_container", "sanic", "setup_dishka"]


def setup_dishka(container: Container | AsyncContainer, app: object) -> None:
    import_module(
        "ashka.integrations." + type(app).__module__.split(".", 1)[0]
    ).setup_dishka(container, app)


def get_container(app: object) -> Container | AsyncContainer:
    return import_module(
        "ashka.integrations." + type(app).__module__.split(".", 1)[0]
    ).get_container(app)
