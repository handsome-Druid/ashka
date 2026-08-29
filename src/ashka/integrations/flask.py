from collections.abc import Callable
from functools import wraps
from importlib.util import find_spec
from typing import Concatenate, ParamSpec, TypeVar

from ashka.container import ContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import Container


def activate(): ...


P = ParamSpec("P")
R = TypeVar("R")

if find_spec("flask"):
    try:
        from dishka.integrations import flask
        from flask import Flask

        __all__: list[str] = ["get_container", "setup_dishka"]

        def _setup_dishka(
            setup_dishka: Callable[Concatenate[Container, Flask, P], R],
        ) -> Callable[Concatenate[Container, Flask, P], R]:
            @wraps(setup_dishka)
            def wrapped(
                container: Container, app: Flask, *args: P.args, **kwargs: P.kwargs
            ) -> R:
                return_: R = setup_dishka(container, app, *args, **kwargs)
                app.extensions["dishka_container"] = container
                return return_

            return wrapped

        flask.setup_dishka = setup_dishka = _setup_dishka(flask.setup_dishka)

        @dishka_setup.register(Flask)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            app: Flask, container: Container, *args: object, **kwargs: object
        ) -> None:
            return setup_dishka(container, app, *args, **kwargs)

        @get_container_.register(Flask)
        def get_container(app: Flask) -> ContainerType:
            return app.extensions["dishka_container"]
    except ImportError:  # pragma: no cover
        pass
