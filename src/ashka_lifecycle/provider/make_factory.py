from collections.abc import Callable
from functools import wraps
from inspect import isbuiltin, isclass, isfunction
from logging import getLogger
from typing import (
    Any,
    NewType,
    ParamSpec,
    TypeVar,
    cast,
    get_origin,
    get_type_hints,
)

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_types,
)
from ashka_lifecycle.entities.scope import AshkaScope

import dishka
from dishka import AnyOf, BaseScope, Scope
from dishka.provider.exceptions import MissingReturnHintError
from dishka.provider.make_factory import (
    _clean_result_hint,  # pyright: ignore[reportPrivateUsage]
    _guess_factory_type,  # pyright: ignore[reportPrivateUsage]
)

__all__: list[str] = ["provide"]

_logger = getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def activate(): ...


def _provide(provide: Callable[P, R]) -> Callable[P, R]:
    @wraps(provide)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        _kwargs = kwargs.copy()
        scope = cast(BaseScope | None, _kwargs.pop("scope", None))
        is_bootstrap = scope is AshkaScope.BOOTSTRAP

        def scoped(source: Any) -> R:
            _logger.debug(
                f"Adding {getattr(source, '__name__', source)!r} to bootstrap list..."
            )

            bootstrap_type = NewType(
                "bootstrap_type",
                AshkaScope,
            )
            if is_bootstrap:
                bootstrap_types.add(bootstrap_type)

            provides = "provides"

            if provides in _kwargs:
                _provides = _kwargs.pop(provides)

                return cast(
                    R,
                    provide(  # pyright: ignore[reportUnknownMemberType]
                        source,  # pyright: ignore[reportCallIssue]
                        scope=Scope.APP if is_bootstrap else scope,  # pyright: ignore[reportCallIssue]
                        provides=AnyOf[bootstrap_type, _provides],  # pyright: ignore[reportCallIssue]
                        **_kwargs,
                    ),
                )

            if isclass(source) or isclass(get_origin(source)):
                return cast(
                    R,
                    provide(  # pyright: ignore[reportUnknownMemberType]
                        source,  # pyright: ignore[reportCallIssue]
                        scope=Scope.APP if is_bootstrap else scope,  # pyright: ignore[reportCallIssue]
                        provides=AnyOf[bootstrap_type, source],  # pyright: ignore[reportCallIssue]
                        **_kwargs,
                    ),
                )

            return_ = "return"

            if isfunction(source) or isbuiltin(source):
                func = source

            elif hasattr(source, "__func__"):
                func = source.__func__

            else:
                func = getattr(source.__call__, "__func__", source.__call__)

            factory_type = _guess_factory_type(func)

            type_hints = get_type_hints(func)

            if return_ not in type_hints:
                raise MissingReturnHintError(source)

            possible_dependency = type_hints[return_]

            type_hint = _clean_result_hint(factory_type, possible_dependency)

            return cast(
                R,
                provide(  # pyright: ignore[reportUnknownMemberType]
                    source,  # pyright: ignore[reportCallIssue]
                    scope=Scope.APP if is_bootstrap else scope,  # pyright: ignore[reportCallIssue]
                    provides=AnyOf[bootstrap_type, type_hint],  # pyright: ignore[reportCallIssue]
                    **_kwargs,
                ),
            )

        source = None

        if args:
            source = args[0]

        if source is None:
            source = kwargs.get("source", None)
        if source is None:
            return cast(R, scoped)

        return scoped(source)

    return wrapped


dishka.provide = dishka.provider.provide = dishka.provider.make_factory.provide = (
    provide
) = _provide(dishka.provide)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType]
