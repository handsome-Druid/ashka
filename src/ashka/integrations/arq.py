from collections.abc import Callable
from importlib.util import find_spec
from typing import Any

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer


def activate(): ...


if find_spec("arq"):
    try:
        from arq import Worker
        from dishka.integrations import arq

        __all__: list[str] = ["get_container", "setup_dishka"]

        @dishka_setup.register(dict)
        @dishka_setup.register(Worker)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            worker_settings: dict[Any, Any] | Worker | Any,
            container: AsyncContainer,
            *args: object,
            **kwargs: object,
        ) -> None:
            arq.setup_dishka(container, worker_settings, *args, **kwargs)

        setup_dishka: Callable[..., None] = arq.setup_dishka

        @get_container_.register(dict)
        @get_container_.register(Worker)
        def get_container(
            worker_setting: dict[Any, Any] | Worker | Any,
        ) -> AsyncContainerType:
            if isinstance(worker_setting, dict):
                return worker_setting["ctx"][arq.DISHKA_APP_CONTAINER_KEY]  # pyright: ignore[reportUnknownVariableType]
            return worker_setting.ctx[arq.DISHKA_APP_CONTAINER_KEY]
    except ImportError:  # pragma: no cover
        pass
