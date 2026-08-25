from collections.abc import AsyncIterator

import pytest
from aiogram import Dispatcher, Router
from ashka.integrations.aiogram import get_container, setup_dishka
from dishka import Provider

from ashka.integrations import get_container as get_dispatch_container
from ashka_lifecycle import (  # pyright: ignore[reportUnknownVariableType]
    make_async_container,
    provide,
)
from ashka_lifecycle.entities.scope import AshkaScope


@pytest.mark.asyncio
async def test_aiogram_bootstrap_lifecycle():
    events: list[str] = []

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        async def resource(self) -> AsyncIterator[str]:
            events.append("initialized")
            yield "resource"
            events.append("closed")

    dispatcher = Dispatcher()
    router = Router()
    container = make_async_container(AppProvider())
    setup_dishka(container, router)
    router.startup.register(container.init)
    router.shutdown.register(container.close)
    dispatcher.include_router(router)

    assert get_container(router) is container
    assert get_dispatch_container(router) is container
    assert events == []

    await dispatcher.emit_startup()

    assert get_container(router) is container
    assert events == ["initialized"]

    await dispatcher.emit_shutdown()

    assert events == ["initialized", "closed"]
