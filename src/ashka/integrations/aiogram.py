from collections.abc import Callable
from functools import wraps
from importlib.util import find_spec
from typing import Concatenate, ParamSpec, TypeVar

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer


def activate(): ...


P = ParamSpec("P")
R = TypeVar("R")

if find_spec("aiogram"):
    try:
        from aiogram import Router
        from dishka.integrations import aiogram

        __all__: list[str] = ["get_container", "setup_dishka"]

        def _setup_dishka(
            setup_dishka: Callable[Concatenate[AsyncContainer, Router, P], R],
        ) -> Callable[Concatenate[AsyncContainer, Router, P], R]:
            @wraps(setup_dishka)
            def wrapped(
                container: AsyncContainer,
                router: Router,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> R:
                return_: R = setup_dishka(container, router, *args, **kwargs)
                router.dishka_container = container  # pyright: ignore[reportAttributeAccessIssue]
                return return_

            return wrapped

        aiogram.setup_dishka = setup_dishka = _setup_dishka(aiogram.setup_dishka)

        @dishka_setup.register(Router)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            router: Router, container: AsyncContainer, *args: object, **kwargs: object
        ) -> None:
            return setup_dishka(container, router, *args, **kwargs)

        @get_container_.register(Router)
        def get_container(router: Router) -> AsyncContainerType:
            return router.dishka_container  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
    except ImportError:  # pragma: no cover
        pass
