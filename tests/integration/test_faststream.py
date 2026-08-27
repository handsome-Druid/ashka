from collections.abc import AsyncIterator

from ashka_lifecycle import (
    AshkaScope,
    provide,  # pyright: ignore[reportUnknownVariableType]
)

import pytest
from ashka.integrations import get_container as get_dispatch_container
from ashka.integrations.faststream import (
    get_container,
    setup_dishka,  # pyright: ignore[reportUnknownVariableType]
)
from dishka import AsyncContainer, FromDishka, Provider, make_async_container
from faststream import FastStream
from faststream.redis import RedisBroker, TestApp, TestRedisBroker


@pytest.mark.asyncio
async def test_faststream_bootstrap_lifecycle():
    events: list[str] = []
    received: list[str] = []

    class Resource:
        value = "resource"

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        async def resource(self) -> AsyncIterator[Resource]:
            events.append("initialized")
            yield Resource()
            events.append("closed")

    broker = RedisBroker()
    app = FastStream(broker)
    container: AsyncContainer = make_async_container(AppProvider())
    setup_dishka(container, app, finalize_container=True, auto_inject=True)

    async def init_container(*_: object):
        await container.__aenter__()

    app.on_startup(init_container)

    @broker.subscriber("test")
    async def handle(_: str, resource: FromDishka[Resource]):
        received.append(resource.value)

    assert get_container(app) is container
    assert get_container(broker) is container
    assert get_dispatch_container(app) is container
    assert get_dispatch_container(broker) is container
    assert events == []

    async with TestRedisBroker(broker), TestApp(app):
        assert events == ["initialized"]
        await broker.publish("message", "test")
        assert received == ["resource"]

    assert events == ["initialized", "closed"]
