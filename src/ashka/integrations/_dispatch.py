from functools import singledispatch

from dishka import AsyncContainer, Container

from ..async_container import AsyncContainerType
from ..container import ContainerType


@singledispatch
def dishka_setup(
    app: object, container: Container | AsyncContainer, *args: object, **kwargs: object
) -> None:
    raise TypeError(
        f"Unsupported application type: {(app_type := type(app)).__module__}.{app_type.__qualname__}"
    )


@singledispatch
def get_container_(app: object) -> ContainerType | AsyncContainerType:
    raise TypeError(
        f"Unsupported application type: {(app_type := type(app)).__module__}.{app_type.__qualname__}"
    )
