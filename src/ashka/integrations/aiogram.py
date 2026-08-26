from collections.abc import Callable
from functools import wraps
from importlib.util import find_spec
from typing import Concatenate

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_
from ashka.integrations._types import P

from dishka import AsyncContainer

if find_spec("aiogram"):
    try:
        from aiogram import Router
        from dishka.integrations import aiogram

        __all__: list[str] = ["get_container", "setup_dishka"]

        _setup_dishka: Callable[..., None] = aiogram.setup_dishka

        def _dishka_setup_(
            _setup_dishka: Callable[Concatenate[AsyncContainer, Router, P], None],
        ):
            @wraps(_setup_dishka)
            def inner(
                router: Router,
                container: AsyncContainer,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                _setup_dishka(container, router, *args, **kwargs)
                router.dishka_container = container  # pyright: ignore[reportAttributeAccessIssue]

            return inner

        def setup_dishka_(
            _dishka_setup: Callable[Concatenate[Router, AsyncContainer, P], None],
        ):
            @wraps(_dishka_setup)
            def inner(
                container: AsyncContainer,
                router: Router,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                _dishka_setup(router, container, *args, **kwargs)

            return inner

        dishka_setup.register(Router)(_dishka_setup := _dishka_setup_(_setup_dishka))

        aiogram.setup_dishka = (setup_dishka := setup_dishka_(_dishka_setup))

        @get_container_.register(Router)
        def get_container(router: Router) -> AsyncContainerType:
            return router.dishka_container  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
    except ImportError:  # pragma: no cover
        pass
