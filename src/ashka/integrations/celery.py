from importlib.util import find_spec

from dishka import Container

from ._dispath import dishka_setup, get_container_

if find_spec("celery"):
    from celery import Celery
    from dishka.integrations import celery

    __all__ = ["get_container", "setup_dishka"]

    @dishka_setup.register(Celery)
    def _dishka_setup(
        app: Celery, container: Container, *args: object, **kwargs: object
    ):
        celery.setup_dishka(container, app, *args, **kwargs)

    def setup_dishka(
        container: Container, app: Celery, *args: object, **kwargs: object
    ) -> None:
        _dishka_setup(app, container, *args, **kwargs)

    @get_container_.register(Celery)
    def get_container(app: Celery) -> Container:
        return app.conf[celery.CONTAINER_NAME]  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
