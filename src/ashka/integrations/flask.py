from collections.abc import Callable
from functools import wraps
from importlib.util import find_spec
from typing import Concatenate

from ashka.container import ContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_
from ashka.integrations._types import P

from dishka import Container

if find_spec("flask"):
    try:
        from dishka.integrations import flask
        from flask import Flask

        __all__: list[str] = ["get_container", "setup_dishka"]

        _setup_dishka: Callable[..., None] = flask.setup_dishka

        def _dishka_setup_(
            _setup_dishka: Callable[Concatenate[Container, Flask, P], None],
        ):
            @wraps(_setup_dishka)
            def inner(
                app: Flask,
                container: Container,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                _setup_dishka(container, app, *args, **kwargs)
                app.extensions["dishka_container"] = container

            return inner

        def setup_dishka_(
            _dishka_setup: Callable[Concatenate[Flask, Container, P], None],
        ):
            @wraps(_dishka_setup)
            def inner(
                container: Container,
                app: Flask,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                _dishka_setup(app, container, *args, **kwargs)

            return inner

        dishka_setup.register(Flask)(_dishka_setup := _dishka_setup_(_setup_dishka))
        setup_dishka: Callable[[Container, Flask], None] = setup_dishka_(_dishka_setup)

        flask.setup_dishka = setup_dishka_(_dishka_setup)

        @get_container_.register(Flask)
        def get_container(app: Flask) -> ContainerType:
            return app.extensions["dishka_container"]
    except ImportError:  # pragma: no cover
        pass
