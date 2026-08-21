from importlib import import_module

from dishka import AsyncContainer, Container

from . import aiohttp, fastapi, flask, litestar, sanic, starlette

__all__ = [
    "aiohttp",
    "fastapi",
    "flask",
    "get_container",
    "litestar",
    "sanic",
    "setup_dishka",
    "starlette",
]


def setup_dishka(container: Container | AsyncContainer, app: object) -> None:
    import_module(
        "ashka.integrations." + type(app).__module__.split(".", 1)[0]
    ).setup_dishka(container, app)


def get_container(app: object) -> Container | AsyncContainer:
    return import_module(
        "ashka.integrations." + type(app).__module__.split(".", 1)[0]
    ).get_container(app)
