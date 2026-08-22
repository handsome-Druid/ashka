from typing import Any, cast

from ashka.entities.bootstrap import (
    bootstrap_keys_by_container,
    bootstrap_sources,  # pyright: ignore[reportUnknownVariableType]
)

import dishka
from dishka import Container as DishkaContainer
from dishka.provider import BaseProvider

__all__ = ["Container", "make_container"]


class Container(DishkaContainer):
    __slots__ = ()

    def __enter__(self):
        enter = super().__enter__()

        if self in bootstrap_keys_by_container:
            for key in bootstrap_keys_by_container[self]:
                self.get(key.type_hint, key.component)

        return enter

    def init(self) -> None:
        self.__enter__()


dishka.Container = dishka.container.Container = Container

_make_container = dishka.make_container


def make_container(*providers: BaseProvider, **kwargs: Any) -> Container:
    bootstrap_keys_by_container[container := _make_container(*providers, **kwargs)] = [
        factory.provides.with_component(provider.component)
        for provider in providers
        for factory in provider.factories
        if getattr(factory.source, "__func__", factory.source) in bootstrap_sources
    ]

    return cast(Container, container)


dishka.make_container = dishka.container.make_container = make_container
