from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from ashka_lifecycle.entities.bootstrap import bootstrap_types
from ashka_lifecycle.entities.scope import AshkaScope

from dishka import Provider, Scope
from dishka.dependency_source import CompositeDependencySource


def activate(): ...


P = ParamSpec("P")
R = TypeVar("R")


def __init__(__init__: Callable[P, R]) -> Callable[P, R]:
    @wraps(__init__)
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        is_bootstrap = False
        args_ = kwargs_ = None
        self = cast(Provider, args[0])
        if len(args) >= 2 and args[1] is AshkaScope.BOOTSTRAP:
            args_ = cast(Any, (self, Scope.APP) + args[2:])
            is_bootstrap = True
        elif kwargs.get("scope", None) is AshkaScope.BOOTSTRAP:
            (kwargs_ := cast(Any, kwargs.copy()))["scope"] = Scope.APP
            is_bootstrap = True
        elif self.scope is AshkaScope.BOOTSTRAP:
            self.scope = Scope.APP
            is_bootstrap = True

        if is_bootstrap:
            for v in type(self).__dict__.values():
                if (
                    isinstance(v, CompositeDependencySource)
                    and v.dependency_sources[1].scope is None  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                ):
                    bootstrap_types.add(v.dependency_sources[1].provides.type_hint)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
        return __init__(*(args_ or args), **(kwargs_ or kwargs))

    return inner


Provider.__init__ = __init__(Provider.__init__)
