from importlib import import_module
from importlib.util import find_spec

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
    if (module := type(app).__module__.split(".", 1)[0]) in _all:
        import_module("ashka.integrations." + module).setup_dishka(
            container, app, *args, **kwargs
        )
    else:
        if find_spec("taskiq"):
            from taskiq import AsyncBroker

            if isinstance(app, AsyncBroker) and isinstance(container, AsyncContainer):
                taskiq.setup_dishka(container, app)
                return
        raise TypeError(
            f"Unsupported application type: {(app_type := type(app)).__module__}.{app_type.__qualname__}"
        )


def get_container(
    app: object, *args: object, **kwargs: object
) -> Container | AsyncContainer:
    if (module := type(app).__module__.split(".", 1)[0]) in _all:
        return import_module("ashka.integrations." + module).get_container(
            app, *args, **kwargs
        )
    else:
        if find_spec("taskiq"):
            from taskiq import AsyncBroker

            if isinstance(app, AsyncBroker):
                return taskiq.get_container(app)
        raise TypeError(
            f"Unsupported application type: {(app_type := type(app)).__module__}.{app_type.__qualname__}"
        )
