from collections.abc import Callable
from functools import wraps
from importlib.util import find_spec
from typing import Any, Concatenate

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_
from ashka.integrations._types import P

from dishka import AsyncContainer

if find_spec("sanic"):
    try:
        from dishka.integrations import sanic
        from sanic import Sanic

        __all__: list[str] = ["get_container", "setup_dishka"]

        _setup_dishka: Callable[..., None] = sanic.setup_dishka

        def _dishka_setup_(
            _setup_dishka: Callable[
                Concatenate[AsyncContainer, Sanic[Any, Any], P], None
            ],
        ):
            @wraps(_setup_dishka)
            def inner(
                app: Sanic[Any, Any],
                container: AsyncContainer,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                _setup_dishka(container, app, *args, **kwargs)
                app.ctx.dishka_container = container

            return inner

        def setup_dishka_(
            _dishka_setup: Callable[
                Concatenate[Sanic[Any, Any], AsyncContainer, P], None
            ],
        ):
            @wraps(_dishka_setup)
            def inner(
                container: AsyncContainer,
                app: Sanic[Any, Any],
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                _dishka_setup(app, container, *args, **kwargs)

            return inner

        dishka_setup.register(Sanic)(_dishka_setup := _dishka_setup_(_setup_dishka))
        setup_dishka: Callable[[AsyncContainer, Sanic[Any, Any]], None] = setup_dishka_(
            _dishka_setup
        )

        sanic.setup_dishka = setup_dishka_(_dishka_setup)

        @get_container_.register(Sanic)
        def get_container(app: Sanic[Any, Any]) -> AsyncContainerType:
            return app.ctx.dishka_container
    except ImportError:  # pragma: no cover
        pass
