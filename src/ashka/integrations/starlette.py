from importlib.util import find_spec

from dishka import AsyncContainer

if find_spec("starlette"):
    from dishka.integrations import starlette
    from starlette.applications import Starlette

    __all__ = ["get_container", "setup_dishka"]

    setup_dishka = starlette.setup_dishka

    def get_container(app: Starlette) -> AsyncContainer:
        return app.state.dishka_container
