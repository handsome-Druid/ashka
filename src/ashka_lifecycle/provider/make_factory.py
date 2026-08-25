from collections.abc import Callable
from typing import Any, get_type_hints, overload

from dishka import BaseScope, Scope
from dishka import provide as _provide  # pyright: ignore[reportUnknownVariableType]
from dishka.dependency_source.composite import CompositeDependencySource
from dishka.entities.provides_marker import ProvideMultiple
from dishka.provider.make_factory import (
    ProvideSource,
    _clean_result_hint,  # pyright: ignore[reportPrivateUsage]
    _guess_factory_type,  # pyright: ignore[reportPrivateUsage]
)

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_sources,  # pyright: ignore[reportUnknownVariableType]
)
from ashka_lifecycle.entities.scope import AshkaScope

__all__ = ["provide"]


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
    if scope is not AshkaScope.BOOTSTRAP:
        return _provide(source, scope=scope, **kwargs)

    def scoped(source: ProvideSource):  # pyright: ignore[reportUnknownParameterType]
        bootstrap_sources.add(func := getattr(source, "__func__", source))  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType, reportUnknownMemberType]
        return (
            _provide(
                source,
                scope=Scope.APP,
                provides=ProvideMultiple[
                    type(str(id(func)), (), {}), kwargs.pop("provides")  # pyright: ignore[reportUnknownArgumentType, reportInvalidTypeArguments]
                ],
                **kwargs,
            )
            if "provides" in kwargs
            else _provide(
                source,
                scope=Scope.APP,
                provides=ProvideMultiple[
                    type(str(id(func)), (), {}),  # pyright: ignore[reportUnknownArgumentType]
                    _clean_result_hint(  # pyright: ignore[reportInvalidTypeArguments]
                        _guess_factory_type(func),
                        get_type_hints(func)["return"],  # pyright: ignore[reportUnknownArgumentType]
                    ),
                ],
                **kwargs,
            )
        )

    if source is not None:
        return scoped(source)

    return scoped  # pyright: ignore[reportUnknownVariableType]
