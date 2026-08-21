from importlib.util import find_spec

from dishka import AsyncContainer

if find_spec("aiohttp"):
    from aiohttp.web_app import Application
    from dishka.integrations import aiohttp

    __all__ = ["get_container", "setup_dishka"]

    setup_dishka = aiohttp.setup_dishka

    def get_container(app: Application) -> AsyncContainer:
        return app[aiohttp.DISHKA_CONTAINER_KEY]
