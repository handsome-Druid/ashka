from ashka.integrations import (
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
from ashka.integrations._dispatch import dishka_setup
from ashka.integrations._dispatch import get_container_ as get_container

from dishka import AsyncContainer, Container

__all__: list[str] = [
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


def setup_dishka(
    container: Container | AsyncContainer, app: object, *args: object, **kwargs: object
) -> None:

    dishka_setup(app, container, *args, **kwargs)
