from collections.abc import AsyncIterator

import pytest
from aiohttp.web import Application
from aiohttp.web_runner import AppRunner
from ashka.integrations.aiohttp import get_container, setup_dishka
from dishka import Provider

from ashka.integrations import get_container as get_dispatch_container
from ashka_lifecycle import (  # pyright: ignore[reportUnknownVariableType]
    make_async_container,
    provide,
)
from ashka_lifecycle.entities.scope import AshkaScope


@pytest.mark.asyncio
async def test_aiohttp_bootstrap_lifecycle():
    events: list[str] = []

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        async def resource(self) -> AsyncIterator[str]:
            events.append("initialized")
            yield "resource"
            events.append("closed")

    app = Application()
    container = make_async_container(AppProvider())
    setup_dishka(container, app)
    _: Application
    app.on_startup.append(lambda _: container.init())
    runner = AppRunner(app)

    assert get_container(app) is container
    assert get_dispatch_container(app) is container
    assert events == []

    await runner.setup()

    assert get_container(app) is container
    assert events == ["initialized"]

    await runner.cleanup()

    assert events == ["initialized", "closed"]
