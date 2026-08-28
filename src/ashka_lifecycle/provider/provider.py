from collections.abc import Callable
from functools import wraps
from typing import Any

from ashka_lifecycle.entities.bootstrap import bootstrap_types
from ashka_lifecycle.entities.scope import AshkaScope

from dishka import Provider, Scope
from dishka.dependency_source import CompositeDependencySource


def activate(): ...


def __init__(__init__: Callable[..., None]) -> Callable[..., None]:
    @wraps(__init__)
    def inner(self: Provider, *args: Any, **kwargs: Any):
        is_bootstrap = False
        args_ = kwargs_ = None
        if args and args[0] is AshkaScope.BOOTSTRAP:
            args_ = (Scope.APP,) + args[1:]
            is_bootstrap = True
        elif kwargs.get("scope", None) is AshkaScope.BOOTSTRAP:
            (kwargs_ := kwargs.copy())["scope"] = Scope.APP
            is_bootstrap = True
        elif self.scope is AshkaScope.BOOTSTRAP:
            self.scope = Scope.APP
            is_bootstrap = True

        if is_bootstrap:
            for v in type(self).__dict__.values():
                if (
                    isinstance(v, CompositeDependencySource)
                    and not v.dependency_sources[1].scope  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                ):
                    bootstrap_types.add(v.dependency_sources[1].provides.type_hint)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
        return __init__(self, *(args_ or args), **(kwargs_ or kwargs))

    return inner


Provider.__init__ = __init__(Provider.__init__)
