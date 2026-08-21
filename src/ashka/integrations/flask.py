from importlib.util import find_spec

from dishka import Container

if find_spec("flask"):
    from dishka.integrations import flask
    from flask import Flask

    __all__ = ["get_container", "setup_dishka"]

    _setup_dishka = flask.setup_dishka

    def setup_dishka(
        container: Container, app: Flask, *args: object, **kwargs: object
    ) -> None:
        _setup_dishka(container, app, *args, **kwargs)
        app.extensions["dishka_container"] = container

    flask.setup_dishka = setup_dishka

    def get_container(app: Flask) -> Container:
        return app.extensions["dishka_container"]
