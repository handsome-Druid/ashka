from logging import getLogger
from os import getenv
from sys import modules

__all__ = [
    "AshkaScope",
    "make_async_container",
    "make_container",
    "provide",
]

if "dishka" in modules and getenv(
    env := "ASHKA_DISABLE_IMPORT_WARNING", ""
).strip().lower() not in ("1", "true", "yes", "on"):
    getLogger(__name__).warning(
        "'dishka' was imported before 'ashka', which may lead to unexpected errors. "
        "Make sure you are using the documented public APIs listed under "
        "'Patched Implementations' in the package documentation "
        "instead of dishka's original implementations, or swap the order."
        f"Set the environment variable '{env}' to disable this warning"
    )

from . import integrations as integrations
from .async_container import make_async_container
from .container import make_container
from .entities.scope import AshkaScope
from .provider import provide  # pyright: ignore[reportUnknownVariableType]
