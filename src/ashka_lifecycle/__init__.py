from ashka_lifecycle.async_container import make_async_container
from ashka_lifecycle.container import make_container
from ashka_lifecycle.entities.scope import AshkaScope
from ashka_lifecycle.provider import (
    provide,  # pyright: ignore[reportUnknownVariableType]
)

__all__: list[str] = [
    "AshkaScope",
    "activate_lifecycle",
    "make_async_container",
    "make_container",
    "provide",
]


def activate_lifecycle() -> None:
    """Activate the ashka lifecycle before lazy imports can defer it.

    Call this function manually before importing dishka to ensure that the
    dishka lifecycle is activated in advance.
    """
