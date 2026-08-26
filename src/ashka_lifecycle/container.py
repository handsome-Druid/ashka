from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, cast

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_keys_by_container,
    bootstrap_types,
)

import dishka
from dishka import Container
from dishka.provider import BaseProvider

__all__: list[str] = ["make_container"]

_enter: Callable[..., Container] = Container.__enter__


def __enter__(self: Container) -> Container:
    enter: Container = _enter(self)

    if self in bootstrap_keys_by_container:
        for key in bootstrap_keys_by_container[self]:
            self.get(key.type_hint, key.component)

    return enter


class ContainerType(Container):
    __slots__ = ()

    __enter__ = __enter__

    def init(self) -> None:
        self.__enter__()


Container.__enter__ = __enter__
Container.init = ContainerType.init  # pyright: ignore[reportAttributeAccessIssue]

_make_container: Callable[..., Container] = dishka.make_container

P = ParamSpec("P")


def make_container_(
    make_container: Callable[P, Container],
) -> Callable[..., ContainerType]:
    @wraps(make_container)
    def inner(*providers: P.args, **kwargs: P.kwargs) -> ContainerType:
        bootstrap_keys_by_container[
            container := _make_container(
                *cast(tuple[BaseProvider, ...], providers), **kwargs
            )
        ] = [
            factory.provides.with_component(provider.component)
            for provider in cast(tuple[BaseProvider, ...], providers)
            for factory in provider.factories
            if factory.provides.type_hint in bootstrap_types
        ]

        return cast(ContainerType, container)

    return inner


dishka.make_container = dishka.container.make_container = (
    make_container := make_container_(_make_container)
)
