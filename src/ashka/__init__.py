from importlib.util import find_spec
from logging import getLogger
from os import getenv
from sys import modules


def activate() -> None:
    """
    Activate the aishka before lazy imports can defer it.

    Call this function manually before importing dishka to ensure that the
    aishka is activated in advance.
    """


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

if find_spec("ashka_lifecycle"):
    from ashka_lifecycle import *  # pyright: ignore[reportWildcardImportFromLibrary]

    activate_lifecycle()
