from importlib.util import find_spec

from dishka import Container

if find_spec("celery"):
    from celery import Celery
    from dishka.integrations import celery

    __all__ = ["get_container", "setup_dishka"]

    setup_dishka = celery.setup_dishka

    def get_container(app: Celery) -> Container:
        return app.conf[celery.CONTAINER_NAME]  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
