from weakref import WeakKeyDictionary, WeakSet

from dishka import AsyncContainer, Container, DependencyKey
from dishka.provider.make_factory import ProvideSource

bootstrap_sources: WeakSet[ProvideSource] = WeakSet()  # pyright: ignore[reportUnknownVariableType]

if all(
    hasattr(Container_, "__weakref__") for Container_ in (Container, AsyncContainer)
):
    bootstrap_keys_by_container: (  # pragma: nocover
        WeakKeyDictionary[
            Container | AsyncContainer,
            set[DependencyKey],
        ]
        | dict[
            Container | AsyncContainer,
            set[DependencyKey],
        ]
    ) = WeakKeyDictionary()

else:
    bootstrap_keys_by_container = {}  # pragma: nocover
