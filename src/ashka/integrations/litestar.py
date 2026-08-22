from importlib.util import find_spec

from dishka import AsyncContainer

from ..async_container import AsyncContainerType
from ._dispatch import dishka_setup, get_container_

if find_spec("litestar"):
    try:
        from dishka.integrations import litestar
        from litestar import Litestar

        __all__ = ["get_container", "setup_dishka"]

        @dishka_setup.register(Litestar)
        def _dishka_setup(
            app: Litestar, container: AsyncContainer, *args: object, **kwargs: object
        ):
            litestar.setup_dishka(container, app, *args, **kwargs)

        setup_dishka = litestar.setup_dishka

        @get_container_.register(Litestar)
        def get_container(app: Litestar) -> AsyncContainerType:
            return app.state.dishka_container
    except ImportError:  # pragma: no cover
        pass
