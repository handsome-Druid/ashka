from importlib.util import find_spec
from typing import Any

from dishka import AsyncContainer

from ._dispatch import dishka_setup, get_container_

if find_spec("arq"):
    try:
        from arq import Worker
        from dishka.integrations import arq

        __all__ = ["get_container", "setup_dishka"]

        @dishka_setup.register(dict)
        @dishka_setup.register(Worker)
        def _dishka_setup(
            worker_settings: dict[Any, Any] | Worker | Any,
            container: AsyncContainer,
            *args: object,
            **kwargs: object,
        ):
            arq.setup_dishka(container, worker_settings, *args, **kwargs)

        setup_dishka = arq.setup_dishka

        @get_container_.register(dict)
        @get_container_.register(Worker)
        def get_container(
            worker_setting: dict[Any, Any] | Worker | Any,
        ) -> AsyncContainer:
            if isinstance(worker_setting, dict):
                return worker_setting["ctx"][arq.DISHKA_APP_CONTAINER_KEY]  # pyright: ignore[reportUnknownVariableType]
            return worker_setting.ctx[arq.DISHKA_APP_CONTAINER_KEY]
    except ImportError:  # pragma: no cover
        pass
