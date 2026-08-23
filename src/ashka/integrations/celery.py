from importlib.util import find_spec

from dishka import Container

from ..container import ContainerType
from ._dispatch import dishka_setup, get_container_

if find_spec("celery"):
    try:
        from celery import Celery # pyright: ignore[reportMissingTypeStubs]
        from dishka.integrations import celery

        __all__ = ["get_container", "setup_dishka"]

        @dishka_setup.register(Celery)
        def _dishka_setup(
            app: Celery, container: Container, *args: object, **kwargs: object
        ):
            celery.setup_dishka(container, app, *args, **kwargs)

        setup_dishka = celery.setup_dishka

        @get_container_.register(Celery)
        def get_container(app: Celery) -> ContainerType:
            return app.conf[celery.CONTAINER_NAME]  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    except ImportError:  # pragma: no cover
        pass
