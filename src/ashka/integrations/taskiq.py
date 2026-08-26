from collections.abc import Callable
from functools import wraps
from importlib.util import find_spec
from typing import Concatenate

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_
from ashka.integrations._types import P

from dishka import AsyncContainer

if find_spec("taskiq"):
    try:
        from dishka.integrations import taskiq
        from taskiq import AsyncBroker

        __all__: list[str] = ["get_container", "setup_dishka"]

        _setup_dishka: Callable[..., None] = taskiq.setup_dishka

        def _dishka_setup_(
            _setup_dishka: Callable[Concatenate[AsyncContainer, AsyncBroker, P], None],
        ):
            @wraps(_setup_dishka)
            def inner(
                broker: AsyncBroker,
                container: AsyncContainer,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                broker.state["dishka_container"] = container
                _setup_dishka(container, broker, *args, **kwargs)

            return inner

        def setup_dishka_(
            _dishka_setup: Callable[Concatenate[AsyncBroker, AsyncContainer, P], None],
        ):
            @wraps(_dishka_setup)
            def inner(
                container: AsyncContainer,
                broker: AsyncBroker,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                _dishka_setup(broker, container, *args, **kwargs)

            return inner

        dishka_setup.register(AsyncBroker)(
            _dishka_setup := _dishka_setup_(_setup_dishka)
        )

        taskiq.setup_dishka = (setup_dishka := setup_dishka_(_dishka_setup))

        @get_container_.register(AsyncBroker)
        def get_container(broker: AsyncBroker) -> AsyncContainerType:
            return broker.state["dishka_container"]
    except ImportError:  # pragma: no cover
        pass
