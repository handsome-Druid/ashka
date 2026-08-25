from collections.abc import Generator
from contextlib import contextmanager

from ashka.integrations import get_container


@contextmanager
def lifespan(app: object) -> Generator[None, None, None]:
    """
    Manage the application container lifecycle.

    Only available when installed with `ashka[lifecycle]`.

    Examples
    --------
    If you need a custom lifespan, copy the entire implementation into your code and modify it there instead of importing `lifespan` from this repository and trying to patch it::

        @contextmanager
        def lifespan(app: object) -> Generator[None, None, None]:
            get_container(app).init()
            try:
                yield
            finally:
                get_container(app).close()

    """
    get_container(app).init()
    try:
        yield
    finally:
        get_container(app).close()
