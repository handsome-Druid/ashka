from importlib.util import find_spec
from typing import Any

from dishka import AsyncContainer

if find_spec("sanic"):
    from dishka.integrations import sanic
    from sanic import Sanic

    __all__ = ["get_container", "setup_dishka"]

    _setup_dishka = sanic.setup_dishka

    def setup_dishka(
        container: AsyncContainer, app: Sanic[Any, Any], *args: object, **kwargs: object
    ) -> None:
        _setup_dishka(container, app, *args, **kwargs)
        app.ctx.dishka_container = container

    sanic.setup_dishka = setup_dishka

    def get_container(app: Sanic[Any, Any]) -> AsyncContainer:
        return app.ctx.dishka_container
