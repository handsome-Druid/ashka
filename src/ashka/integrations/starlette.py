from collections.abc import Callable
from importlib.util import find_spec

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer


def activate(): ...


if find_spec("starlette"):
    try:
        from dishka.integrations import starlette
        from starlette.applications import Starlette

        __all__: list[str] = ["get_container", "setup_dishka"]

        @dishka_setup.register(Starlette)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            app: Starlette, container: AsyncContainer, *args: object, **kwargs: object
        ) -> None:
            starlette.setup_dishka(container, app, *args, **kwargs)

        setup_dishka: Callable[..., None] = starlette.setup_dishka

        @get_container_.register(Starlette)
        def get_container(app: Starlette) -> AsyncContainerType:
            return app.state.dishka_container
    except ImportError:  # pragma: no cover
        pass
