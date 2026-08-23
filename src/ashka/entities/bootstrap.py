from weakref import WeakSet

from dishka import AsyncContainer, Container, DependencyKey
from dishka.provider.make_factory import ProvideSource

bootstrap_sources: WeakSet[ProvideSource] = WeakSet()  # pyright: ignore[reportUnknownVariableType]

bootstrap_keys_by_container: dict[
    Container | AsyncContainer,
    list[DependencyKey],
] = {}
