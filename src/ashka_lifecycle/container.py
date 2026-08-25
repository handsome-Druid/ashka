from typing import Any, cast

import dishka
from dishka import Container, DependencyKey
from dishka.provider import BaseProvider

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_keys_by_container,
    bootstrap_sources,  # pyright: ignore[reportUnknownVariableType]
)

__all__ = ["make_container"]

_enter = Container.__enter__


def __enter__(self: Container):
    enter = _enter(self)

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

_make_container = dishka.make_container


def make_container(*providers: BaseProvider, **kwargs: Any) -> ContainerType:
    container_key: set[DependencyKey] = set()

    for provider in providers:
        for factory in provider.factories:
            if (
                source := getattr(factory.source, "__func__", factory.source)
                in bootstrap_sources
            ):
                if (
                    key := factory.provides.with_component(provider.component)
                ) in container_key:
                    raise ValueError(
                        f"{source} with component: {key.component} and type hint: {key.type_hint} conflicts with other factories."
                    )
                container_key.add(key)

    bootstrap_keys_by_container[container := _make_container(*providers, **kwargs)] = (
        container_key
    )

    return cast(ContainerType, container)


dishka.make_container = dishka.container.make_container = make_container
