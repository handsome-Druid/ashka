from collections.abc import Callable

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_types,
)

from dishka import Container


def activate(): ...


_enter: Callable[..., Container] = Container.__enter__


def __enter__(self: Container) -> Container:
    enter: Container = _enter(self)

    [
        self.get(key.type_hint, key.component)
        for registry in iter(
            lambda state=[self.registry]: (
                (state[0], state.__setitem__(0, state[0].child_registry))[0]  # pyright: ignore[reportCallIssue, reportArgumentType]
                if state[0] is not None  # pyright: ignore[reportUnnecessaryComparison]
                else None
            ),
            None,
        )
        for key in registry.factories
        if key.type_hint in bootstrap_types
    ]

    return enter


def init(self: Container) -> None:
    self.__enter__()


Container.__enter__ = __enter__
Container.init = init  # pyright: ignore[reportAttributeAccessIssue]
