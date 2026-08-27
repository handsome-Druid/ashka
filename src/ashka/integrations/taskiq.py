from collections.abc import Callable
from importlib.util import find_spec

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer


def activate(): ...


if find_spec("taskiq"):
    try:
        from dishka.integrations import taskiq
        from taskiq import AsyncBroker

        __all__: list[str] = ["get_container", "setup_dishka"]

        _setup_dishka: Callable[..., None] = taskiq.setup_dishka

        @dishka_setup.register(AsyncBroker)
        def _dishka_setup(
            broker: AsyncBroker,
            container: AsyncContainer,
            *args: object,
            **kwargs: object,
        ) -> None:
            _setup_dishka(container, broker, *args, **kwargs)
            broker.state["dishka_container"] = container

        def setup_dishka(
            container: AsyncContainer,
            broker: AsyncBroker,
            *args: object,
            **kwargs: object,
        ) -> None:
            _dishka_setup(broker, container, *args, **kwargs)

        taskiq.setup_dishka = setup_dishka

        @get_container_.register(AsyncBroker)
        def get_container(broker: AsyncBroker) -> AsyncContainerType:
            return broker.state["dishka_container"]
    except ImportError:  # pragma: no cover
        pass
