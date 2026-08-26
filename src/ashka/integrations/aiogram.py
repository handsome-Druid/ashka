from importlib.util import find_spec

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer

if find_spec("aiogram"):
    try:
        from aiogram import Router
        from dishka.integrations import aiogram

        __all__: list[str] = ["get_container", "setup_dishka"]

        _setup_dishka = aiogram.setup_dishka

        @dishka_setup.register(Router)
        def _dishka_setup(
            router: Router, container: AsyncContainer, *args: object, **kwargs: object
        ) -> None:
            _setup_dishka(container, router, *args, **kwargs)
            router.dishka_container = container  # pyright: ignore[reportAttributeAccessIssue]

        def setup_dishka(
            container: AsyncContainer, router: Router, *args: object, **kwargs: object
        ) -> None:
            _dishka_setup(router, container, *args, **kwargs)

        aiogram.setup_dishka = setup_dishka

        @get_container_.register(Router)
        def get_container(router: Router) -> AsyncContainerType:
            return router.dishka_container  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
    except ImportError:  # pragma: no cover
        pass
