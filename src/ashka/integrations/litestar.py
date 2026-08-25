from collections.abc import Callable
from importlib.util import find_spec

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer
from dishka.integrations.litestar import setup_dishka

if find_spec("litestar"):
    try:
        from dishka.integrations import litestar
        from litestar import Litestar

        __all__: list[str] = ["get_container", "setup_dishka"]

        @dishka_setup.register(Litestar)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            app: Litestar, container: AsyncContainer, *args: object, **kwargs: object
        ) -> None:
            litestar.setup_dishka(container, app, *args, **kwargs)

        setup_dishka: Callable[..., None] = litestar.setup_dishka

        @get_container_.register(Litestar)
        def get_container(app: Litestar) -> AsyncContainerType:
            return app.state.dishka_container
    except ImportError:  # pragma: no cover
        pass
