from collections.abc import Generator
from contextlib import contextmanager

from ashka.integrations import get_container

from dishka import Container


@contextmanager
def lifespan(app: object) -> Generator[None, None, None]:
    """
    Manage the application container lifecycle.

    Installing `ashka[lifecycle]` automatically attaches `container.init()` to the
    lifespan.

    Examples
    --------
    If you need a custom lifespan, copy the example implementation into your code and modify it there instead of importing `lifespan` from this repository and trying to patch it::

        @contextmanager
        def lifespan(app: object) -> Generator[None, None, None]:
            with get_container(app):
                yield
    """
    if not isinstance(container := get_container(app), Container):
        raise TypeError(f"{type(Container)} is not a sync container!")
    with container:
        yield
