import ashka_lifecycle.async_container
import ashka_lifecycle.container
import ashka_lifecycle.provider
import ashka_lifecycle.provider.make_factory
import ashka_lifecycle.provider.provider
from ashka_lifecycle.entities.scope import AshkaScope
from ashka_lifecycle.provider import (
    provide,  # pyright: ignore[reportUnknownVariableType]
)

__all__: list[str] = [
    "AshkaScope",
    "activate_lifecycle",
    "provide",
]


def activate_lifecycle() -> None:
    """Activate the ashka lifecycle before lazy imports can defer it.

    Call this function manually before importing dishka to ensure that the
    dishka lifecycle is activated in advance.
    """
    ashka_lifecycle.container.activate()
    ashka_lifecycle.async_container.activate()
    ashka_lifecycle.provider.provider.activate()
    ashka_lifecycle.provider.make_factory.activate()
