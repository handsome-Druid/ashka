from collections.abc import Callable
from importlib.util import find_spec

from ashka.container import ContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import Container
from dishka.integrations.celery import setup_dishka

if find_spec("celery"):
    try:
        from celery import Celery  # pyright: ignore[reportMissingTypeStubs]
        from dishka.integrations import celery

        __all__: list[str] = ["get_container", "setup_dishka"]

        @dishka_setup.register(Celery)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            app: Celery, container: Container, *args: object, **kwargs: object
        ) -> None:
            celery.setup_dishka(container, app, *args, **kwargs)

        setup_dishka: Callable[..., None] = celery.setup_dishka

        @get_container_.register(Celery)
        def get_container(app: Celery) -> ContainerType:
            return app.conf[celery.CONTAINER_NAME]  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    except ImportError:  # pragma: no cover
        pass
