from .async_container import make_async_container
from .container import make_container
from .entities.scope import AshkaScope
from .provider import provide  # pyright: ignore[reportUnknownVariableType]

__all__ = [
    "AshkaScope",
    "activate_lifecycle",
    "make_async_container",
    "make_container",
    "provide",
]


def activate_lifecycle():
    """Activate the ashka lifecycle before lazy imports can defer it.

    Call this function manually before importing dishka to ensure that the
    dishka lifecycle is activated in advance.
    """
