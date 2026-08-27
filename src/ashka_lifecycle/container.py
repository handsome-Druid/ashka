from collections.abc import Callable
from logging import getLogger

from ashka_lifecycle.entities.bootstrap import (
    bootstrap_types,
)

from dishka import Container, Scope


def activate(): ...


_logger = getLogger(__name__)

_enter: Callable[..., Container] = Container.__enter__


def __enter__(self: Container) -> Container:
    enter: Container = _enter(self)

    if self.scope is Scope.APP:
        _logger.debug("Initiating bootstrap factories.")
        for key in self.registry.factories:
            if key.type_hint in bootstrap_types:
                self.get(key.type_hint, key.component)
    else:
        _logger.debug(
            f"'<dishka_container>.scope': {self.scope!r} is not 'Scope.APP', skipping bootstrap"
        )

    return enter


def init(self: Container) -> None:
    if not self.scope is Scope.APP:
        _logger.warning(
            f"'<dishka_container>.scope': {self.scope!r} is not 'Scope.APP', 'container.init()' won't do any bootstrap."
        )
    self.__enter__()


Container.__enter__ = __enter__
Container.init = init  # pyright: ignore[reportAttributeAccessIssue]
