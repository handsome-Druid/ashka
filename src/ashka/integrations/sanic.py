from collections.abc import Callable
from functools import wraps
from importlib.util import find_spec
from typing import Any, Concatenate, ParamSpec, TypeVar

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer


def activate(): ...


P = ParamSpec("P")
R = TypeVar("R")

if find_spec("sanic"):
    try:
        from dishka.integrations import sanic
        from sanic import Sanic

        __all__: list[str] = ["get_container", "setup_dishka"]

        def _setup_dishka(
            setup_dishka: Callable[Concatenate[AsyncContainer, Sanic[Any, Any], P], R],
        ) -> Callable[Concatenate[AsyncContainer, Sanic[Any, Any], P], R]:
            @wraps(setup_dishka)
            def wrapped(
                container: AsyncContainer,
                app: Sanic[Any, Any],
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> R:
                return_: R = setup_dishka(container, app, *args, **kwargs)
                app.ctx.dishka_container = container
                return return_

            return wrapped

        sanic.setup_dishka = setup_dishka = _setup_dishka(sanic.setup_dishka)

        @dishka_setup.register(Sanic)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            app: Sanic[Any, Any],
            container: AsyncContainer,
            *args: object,
            **kwargs: object,
        ) -> None:
            return setup_dishka(container, app, *args, **kwargs)

        @get_container_.register(Sanic)
        def get_container(app: Sanic[Any, Any]) -> AsyncContainerType:
            return app.ctx.dishka_container
    except ImportError:  # pragma: no cover
        pass
