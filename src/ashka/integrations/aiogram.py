from importlib.util import find_spec

from dishka import AsyncContainer

if find_spec("aiogram"):
    from aiogram import Router
    from dishka.integrations import aiogram

    __all__ = ["get_container", "setup_dishka"]

    _setup_dishka = aiogram.setup_dishka

    def setup_dishka(
        container: AsyncContainer, router: Router, *args: object, **kwargs: object
    ) -> None:
        _setup_dishka(container, router, *args, **kwargs)
        router.dishka_container = container  # pyright: ignore[reportAttributeAccessIssue]

    aiogram.setup_dishka = setup_dishka

    def get_container(router: Router) -> AsyncContainer:
        return router.dishka_container  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
