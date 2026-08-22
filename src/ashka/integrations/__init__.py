from dishka import AsyncContainer, Container

from . import (
    aiogram,
    aiohttp,
    celery,
    fastapi,
    flask,
    litestar,
    sanic,
    starlette,
    taskiq,
)
from ._dispath import dishka_setup
from ._dispath import get_container_ as get_container

__all__ = [
    "aiogram",
    "aiohttp",
    "celery",
    "fastapi",
    "flask",
    "get_container",
    "litestar",
    "sanic",
    "setup_dishka",
    "starlette",
    "taskiq",
]


_all = list(__all__)
_all.remove("taskiq")
_all.remove("get_container")
_all.remove("setup_dishka")


def setup_dishka(
    container: Container | AsyncContainer, app: object, *args: object, **kwargs: object
) -> None:

    dishka_setup(app, container, *args, **kwargs)
