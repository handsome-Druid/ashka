from collections.abc import Callable
from typing import Any, overload

from ashka.entities.bootstrap import (
    bootstrap_sources,  # pyright: ignore[reportUnknownVariableType]
)
from ashka.entities.scope import AshkaScope

from dishka import BaseScope, Scope
from dishka import provide as _provide  # pyright: ignore[reportUnknownVariableType]
from dishka.dependency_source.composite import CompositeDependencySource
from dishka.provider.make_factory import ProvideSource

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
        bootstrap_sources.add(getattr(source, "__func__", source))  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        return _provide(source, scope=Scope.APP, **kwargs)

    if source is not None:
        return scoped(source)

    return scoped  # pyright: ignore[reportUnknownVariableType]
