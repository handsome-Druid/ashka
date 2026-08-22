from dishka import AsyncContainer, Container

from . import (
    aiogram,
    aiohttp,
    arq,
    celery,
    click,
    fastapi,
    flask,
    litestar,
    sanic,
    starlette,
    taskiq,
    telebot,
)
from ._dispatch import dishka_setup
from ._dispatch import get_container_ as get_container

__all__ = [
    "aiogram",
    "aiohttp",
    "arq",
    "celery",
    "click",
    "fastapi",
    "flask",
    "get_container",
    "litestar",
    "sanic",
    "setup_dishka",
    "starlette",
    "taskiq",
    "telebot",
]


_all = list(__all__)
_all.remove("taskiq")
_all.remove("get_container")
_all.remove("setup_dishka")


def setup_dishka(
    container: Container | AsyncContainer, app: object, *args: object, **kwargs: object
) -> None:

    dishka_setup(app, container, *args, **kwargs)
