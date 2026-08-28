from collections.abc import Callable
from inspect import isbuiltin, isclass, isfunction
from logging import getLogger
from typing import Any, NewType, get_origin, get_type_hints, overload

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_types,
)
from ashka_lifecycle.entities.scope import AshkaScope

import dishka
from dishka import AnyOf, BaseScope, Scope
from dishka import provide as _provide  # pyright: ignore[reportUnknownVariableType]
from dishka.dependency_source.composite import CompositeDependencySource
from dishka.provider.exceptions import MissingReturnHintError
from dishka.provider.make_factory import (
    ProvideSource,
    _clean_result_hint,  # pyright: ignore[reportPrivateUsage]
    _guess_factory_type,  # pyright: ignore[reportPrivateUsage]
)

__all__: list[str] = ["provide"]

_logger = getLogger(__name__)


def activate(): ...


@overload
def provide(
    *, scope: BaseScope | AshkaScope | None = None, **kwargs: Any
) -> Callable[[Callable[..., Any]], CompositeDependencySource]: ...


@overload
def provide(
    source: ProvideSource,  # pyright: ignore[reportUnknownParameterType]
    *,
    scope: BaseScope | AshkaScope | None = None,
    **kwargs: Any,
) -> CompositeDependencySource: ...


def provide(
    source: ProvideSource | None = None,  # pyright: ignore[reportUnknownParameterType]
    *,
    scope: BaseScope | AshkaScope | None = None,
    **kwargs: Any,
) -> (
    CompositeDependencySource
    | Callable[
        [Callable[..., Any]],
        CompositeDependencySource,
    ]
):

    is_bootstrap = scope is AshkaScope.BOOTSTRAP

    def scoped(source: Any) -> CompositeDependencySource:
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

        if provides in kwargs:
            _kwargs = kwargs.copy()

            _provides = _kwargs.pop(provides)

            return _provide(
                source,
                scope=Scope.APP if is_bootstrap else scope,
                provides=AnyOf[bootstrap_type, _provides],
                **_kwargs,
            )

        if isclass(source) or isclass(get_origin(source)):
            return _provide(
                source,
                scope=Scope.APP if is_bootstrap else scope,
                provides=AnyOf[bootstrap_type, source],
                **kwargs,
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

        return _provide(
            source,
            scope=Scope.APP if is_bootstrap else scope,
            provides=AnyOf[bootstrap_type, type_hint],
            **kwargs,
        )

    if source is None:
        return scoped

    return scoped(source)


dishka.provide = dishka.provider.provide = dishka.provider.make_factory.provide = (
    provide
)
