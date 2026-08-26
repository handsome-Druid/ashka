from types import FunctionType
from weakref import WeakKeyDictionary, WeakSet

from dishka import AsyncContainer, Container, DependencyKey

if all(
    hasattr(Container_, "__weakref__") for Container_ in (Container, AsyncContainer)
):
    bootstrap_keys_by_container: (  # pragma: nocover
        WeakKeyDictionary[
            Container | AsyncContainer,
            list[DependencyKey],
        ]
        | dict[
            Container | AsyncContainer,
            list[DependencyKey],
        ]
    ) = WeakKeyDictionary()

else:
    bootstrap_keys_by_container = {}  # pragma: nocover

bootstrap_types: WeakSet[FunctionType] = WeakSet()
