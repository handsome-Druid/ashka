from importlib.util import find_spec

from dishka import AsyncContainer

from ._dispatch import dishka_setup, get_container_

if find_spec("aiogram"):
    from aiogram import Router
    from dishka.integrations import aiogram

    __all__ = ["get_container", "setup_dishka"]

    _setup_dishka = aiogram.setup_dishka

    @dishka_setup.register(Router)
    def _dishka_setup(
        router: Router, container: AsyncContainer, *args: object, **kwargs: object
    ):
        _setup_dishka(container, router, *args, **kwargs)
        router.dishka_container = container  # pyright: ignore[reportAttributeAccessIssue]

    def setup_dishka(container: AsyncContainer, router: Router) -> None:
        _dishka_setup(router, container)

    aiogram.setup_dishka = setup_dishka

    @get_container_.register(Router)
    def get_container(router: Router) -> AsyncContainer:
        return router.dishka_container  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
