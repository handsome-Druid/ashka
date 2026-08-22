from importlib.util import find_spec

from dishka import AsyncContainer

from ._dispatch import dishka_setup, get_container_

if find_spec("starlette"):
    from dishka.integrations import starlette
    from starlette.applications import Starlette

    __all__ = ["get_container", "setup_dishka"]

    @dishka_setup.register(Starlette)
    def _dishka_setup(
        app: Starlette, container: AsyncContainer, *args: object, **kwargs: object
    ):
        starlette.setup_dishka(container, app, *args, **kwargs)

    setup_dishka = starlette.setup_dishka

    @get_container_.register(Starlette)
    def get_container(app: Starlette) -> AsyncContainer:
        return app.state.dishka_container
