from importlib.util import find_spec

from ashka.container import ContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import Container

if find_spec("flask"):
    try:
        from dishka.integrations import flask
        from flask import Flask

        __all__: list[str] = ["get_container", "setup_dishka"]

        _setup_dishka = flask.setup_dishka

        @dishka_setup.register(Flask)
        def _dishka_setup(
            app: Flask, container: Container, *args: object, **kwargs: object
        ) -> None:
            _setup_dishka(container, app, *args, **kwargs)
            app.extensions["dishka_container"] = container

        def setup_dishka(
            container: Container, app: Flask, *args: object, **kwargs: object
        ) -> None:
            _dishka_setup(app, container, *args, **kwargs)

        flask.setup_dishka = setup_dishka

        @get_container_.register(Flask)
        def get_container(app: Flask) -> ContainerType:
            return app.extensions["dishka_container"]
    except ImportError:  # pragma: no cover
        pass
