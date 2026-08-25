from importlib.util import find_spec
from logging import getLogger
from os import getenv
from sys import modules
from typing import Any

from ashka.async_container import AsyncContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import AsyncContainer

if "dishka.integrations.faststream" in modules and getenv(
    env := "ASHKA_DISABLE_IMPORT_WARNING", ""
).strip().lower() not in ("1", "true", "yes", "on"):
    getLogger(__name__).warning(
        "'dishka.integrations.faststream' was imported before "
        "'ashka.integrations.faststream', which may lead to unexpected errors. "
        "Import 'ashka.integrations.faststream' first so its patches are applied. "
        f"Set the environment variable '{env}' to disable this warning"
    )

# Add the FastStream availability check here if automatic imports are restored.
from dishka.integrations import faststream
from faststream import FastStream
from faststream.__about__ import (
    __version__ as FASTSTREAM_VERSION,
)

if FASTSTREAM_VERSION.startswith("0.5"):
    from dishka.integrations.faststream import faststream_05 as faststream_
    from dishka.integrations.faststream.faststream_05 import (
        Application,  # pyright: ignore[reportUnknownVariableType]
        ApplicationLike,
    )
    from faststream.broker.core.usecase import (  # pyright: ignore[reportMissingImports]
        BrokerUsecase as BrokerType,  # pyright: ignore[reportUnknownVariableType]
    )
elif FASTSTREAM_VERSION.startswith(("0.6", "0.7")):
    from dishka.integrations.faststream import faststream_06 as faststream_
    from dishka.integrations.faststream.faststream_06 import (
        Application,  # pyright: ignore[reportUnknownVariableType]
        ApplicationLike,
    )
    from faststream._internal.broker import (  # pyright: ignore[reportMissingImports]
        BrokerUsecase as BrokerType,  # pyright: ignore[reportUnknownVariableType]
    )
else:
    assert False, "unreachable"

__all__: list[str] = ["get_container", "setup_dishka"]

_setup_dishka = faststream_.setup_dishka  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]


@dishka_setup.register(FastStream)
def _app_setup(
    app: "Application | ApplicationLike",  # pyright: ignore[reportUnknownParameterType]
    container: AsyncContainer,
    *args: object,
    **kwargs: object,
) -> None:
    _setup_dishka(container, app, None, *args, **kwargs)
    app.broker.dishka_container = container  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue, reportUnknownMemberType]


@dishka_setup.register(BrokerType)  # pyright: ignore[reportUnknownArgumentType]
def _broker_setup(
    broker: "BrokerType[Any, Any]",  # pyright: ignore[reportUnknownParameterType]
    container: AsyncContainer,
    *args: object,
    **kwargs: object,
) -> None:
    _setup_dishka(container, None, broker, *args, **kwargs)  # pyright: ignore[reportUnknownArgumentType]
    broker.dishka_container = container  # pyright: ignore[reportAttributeAccessIssue]


def setup_dishka(
    container: AsyncContainer,
    app: "Application | ApplicationLike | None" = None,  # pyright: ignore[reportUnknownParameterType]
    broker: "BrokerType[Any, Any] | None" = None,  # pyright: ignore[reportUnknownParameterType]
    *args: object,
    **kwargs: object,
) -> None:
    if app and not broker:
        _app_setup(app, container, *args, **kwargs)
        return

    if broker and not app:
        _broker_setup(broker, container, *args, **kwargs)
        return

    raise ValueError(
        "You must provide either app or broker to setup dishka integration.",
    )


faststream.setup_dishka = faststream_.setup_dishka = setup_dishka


@get_container_.register(FastStream)
@get_container_.register(BrokerType)  # pyright: ignore[reportUnknownArgumentType]
def get_container(
    app_or_broker: "Application | ApplicationLike | BrokerType[Any, Any]",  # pyright: ignore[reportUnknownParameterType]
) -> AsyncContainerType:
    if hasattr(app_or_broker, "dishka_container"):  # pyright: ignore[reportUnknownArgumentType]
        return app_or_broker.dishka_container  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
    return app_or_broker.broker.dishka_container  # pyright: ignore[reportUnknownVariableType, reportOptionalMemberAccess, reportUnknownMemberType, reportAttributeAccessIssue]


try:
    from faststream.asgi import (
        AsgiFastStream,  # pyright: ignore[reportUnknownVariableType, reportMissingImports]
    )

    dishka_setup.register(AsgiFastStream)(_app_setup)  # pyright: ignore[reportUnknownArgumentType]
    get_container_.register(AsgiFastStream)(get_container)  # pyright: ignore[reportUnknownArgumentType]
except ImportError:
    pass

if find_spec("fastapi"):
    try:
        if FASTSTREAM_VERSION.startswith("0.5"):
            from faststream.broker.fastapi import (  # pyright: ignore[reportMissingImports]
                StreamRouter,  # pyright: ignore[reportUnknownVariableType]
            )
        elif FASTSTREAM_VERSION.startswith(("0.6", "0.7")):
            from faststream._internal.fastapi import (  # pyright: ignore[reportMissingImports]
                StreamRouter,  # pyright: ignore[reportUnknownVariableType]
            )
        else:
            assert False, "unreachable"
        dishka_setup.register(StreamRouter)(_app_setup)  # pyright: ignore[reportUnknownArgumentType]
        get_container_.register(StreamRouter)(get_container)  # pyright: ignore[reportUnknownArgumentType]
    except ImportError:
        pass
