from importlib.util import find_spec

from dishka import AsyncContainer

if find_spec("litestar"):
    from dishka.integrations import litestar
    from litestar import Litestar

    __all__ = ["get_container", "setup_dishka"]

    setup_dishka = litestar.setup_dishka

    def get_container(app: Litestar) -> AsyncContainer:
        return app.state.dishka_container
