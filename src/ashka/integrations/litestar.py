from importlib.util import find_spec

from dishka import AsyncContainer

from ._dispatch import dishka_setup, get_container_

if find_spec("litestar"):
    from dishka.integrations import litestar
    from litestar import Litestar

    __all__ = ["get_container", "setup_dishka"]

    @dishka_setup.register(Litestar)
    def _dishka_setup(
        app: Litestar, container: AsyncContainer, *args: object, **kwargs: object
    ):
        litestar.setup_dishka(container, app, *args, **kwargs)

    def setup_dishka(
        container: AsyncContainer, app: Litestar, *args: object, **kwargs: object
    ) -> None:
        _dishka_setup(app, container, *args, **kwargs)

    @get_container_.register(Litestar)
    def get_container(app: Litestar) -> AsyncContainer:
        return app.state.dishka_container
