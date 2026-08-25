from importlib.util import find_spec
from typing import Any

from dishka import AsyncContainer

from ..async_container import AsyncContainerType
from ._dispatch import dishka_setup, get_container_

if find_spec("sanic"):
    try:
        from dishka.integrations import sanic
        from sanic import Sanic

        __all__ = ["get_container", "setup_dishka"]

        _setup_dishka = sanic.setup_dishka

        @dishka_setup.register(Sanic)
        def _dishka_setup(
            app: Sanic[Any, Any],
            container: AsyncContainer,
            *args: object,
            **kwargs: object,
        ):
            _setup_dishka(container, app, *args, **kwargs)
            app.ctx.dishka_container = container

        def setup_dishka(
            container: AsyncContainer,
            app: Sanic[Any, Any],
            *args: object,
            **kwargs: object,
        ) -> None:
            _dishka_setup(app, container, *args, **kwargs)

        sanic.setup_dishka = setup_dishka

        @get_container_.register(Sanic)
        def get_container(app: Sanic[Any, Any]) -> AsyncContainerType:
            return app.ctx.dishka_container
    except ImportError:  # pragma: no cover
        pass
