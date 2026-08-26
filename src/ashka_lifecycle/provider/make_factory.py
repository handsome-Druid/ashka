from collections.abc import Callable
from typing import Any, NewType, get_type_hints, overload

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_types,
)
from ashka_lifecycle.entities.scope import AshkaScope

from dishka import BaseScope, Scope
from dishka import provide as _provide  # pyright: ignore[reportUnknownVariableType]
from dishka.dependency_source.composite import CompositeDependencySource
from dishka.entities.provides_marker import ProvideMultiple
from dishka.provider.make_factory import (
    ProvideSource,
    _clean_result_hint,  # pyright: ignore[reportPrivateUsage]
    _guess_factory_type,  # pyright: ignore[reportPrivateUsage]
)

__all__: list[str] = ["provide"]


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

    def scoped(source: ProvideSource) -> CompositeDependencySource:  # pyright: ignore[reportUnknownParameterType]
        return (
            _provide(
                source,
                scope=Scope.APP,
                provides=ProvideMultiple[
                    new_type, (_kwargs := kwargs.copy()).pop("provides")  # pyright: ignore[reportUnknownArgumentType, reportInvalidTypeArguments, reportArgumentType]
                ],
                **_kwargs,
            )
            if not bootstrap_types.add(new_type := NewType("_", object))
            and "provides" in kwargs
            else _provide(
                source,
                scope=Scope.APP,
                provides=ProvideMultiple[
                    new_type,  # pyright: ignore[reportUnknownArgumentType, reportArgumentType]
                    _clean_result_hint(  # pyright: ignore[reportInvalidTypeArguments]
                        _guess_factory_type(
                            func := getattr(source, "__func__", source)  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
                        ),
                        get_type_hints(func)["return"],  # pyright: ignore[reportUnknownArgumentType]
                    ),
                ],
                **kwargs,
            )
        )

    return scoped if source is None else scoped(source)  # pyright: ignore[reportUnknownVariableType]
