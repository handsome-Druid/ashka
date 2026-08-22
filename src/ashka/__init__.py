from logging import getLogger
from os import getenv
from sys import modules

__all__ = [
    "BOOTSTRAP",
    "AsyncContainer",
    "Container",
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

from . import async_container as _async_container
from . import container as _container
from . import integrations as integrations
from .entities.scope import BOOTSTRAP
from .provider import provide  # pyright: ignore[reportUnknownVariableType]

AsyncContainer = _async_container.AsyncContainer
Container = _container.Container
make_async_container = _async_container.make_async_container
make_container = _container.make_container
