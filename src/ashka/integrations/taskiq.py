from collections.abc import Callable
from functools import wraps
from importlib.util import find_spec
from typing import Concatenate, ParamSpec, TypeVar

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer


def activate(): ...


P = ParamSpec("P")
R = TypeVar("R")

if find_spec("taskiq"):
    try:
        from dishka.integrations import taskiq
        from taskiq import AsyncBroker

        __all__: list[str] = ["get_container", "setup_dishka"]

        def _setup_dishka(
            setup_dishka: Callable[Concatenate[AsyncContainer, AsyncBroker, P], R],
        ) -> Callable[Concatenate[AsyncContainer, AsyncBroker, P], R]:
            @wraps(setup_dishka)
            def wrapped(
                container: AsyncContainer,
                broker: AsyncBroker,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> R:
                return_: R = setup_dishka(container, broker, *args, **kwargs)
                broker.state["dishka_container"] = container
                return return_

            return wrapped

        taskiq.setup_dishka = setup_dishka = _setup_dishka(taskiq.setup_dishka)

        @dishka_setup.register(AsyncBroker)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            broker: AsyncBroker,
            container: AsyncContainer,
            *args: object,
            **kwargs: object,
        ) -> None:
            return setup_dishka(container, broker, *args, **kwargs)

        @get_container_.register(AsyncBroker)
        def get_container(broker: AsyncBroker) -> AsyncContainerType:
            return broker.state["dishka_container"]
    except ImportError:  # pragma: no cover
        pass
