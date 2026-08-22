from importlib.util import find_spec

from dishka import AsyncContainer

from ._dispatch import dishka_setup, get_container_

if find_spec("aiohttp"):
    try:
        from aiohttp.web_app import Application
        from dishka.integrations import aiohttp

        __all__ = ["get_container", "setup_dishka"]

        @dishka_setup.register(Application)
        def _dishka_setup(
            app: Application, container: AsyncContainer, *args: object, **kwargs: object
        ):
            aiohttp.setup_dishka(container, app, *args, **kwargs)

        setup_dishka = aiohttp.setup_dishka

        @get_container_.register(Application)
        def get_container(app: Application) -> AsyncContainer:
            return app[aiohttp.DISHKA_CONTAINER_KEY]
    except ImportError:  # pragma: no cover
        pass
