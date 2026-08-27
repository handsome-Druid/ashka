from collections.abc import AsyncIterator

from ashka_lifecycle import (
    AshkaScope,
    provide,  # pyright: ignore[reportUnknownVariableType]
)

import pytest
from ashka.integrations import get_container as get_dispatch_container
from ashka.integrations.taskiq import get_container, setup_dishka
from dishka import AsyncContainer, FromDishka, Provider, make_async_container
from dishka.integrations.taskiq import inject
from taskiq import InMemoryBroker, TaskiqEvents


@pytest.mark.asyncio
async def test_taskiq_bootstrap_lifecycle():
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

    broker = InMemoryBroker(await_inplace=True)
    container: AsyncContainer = make_async_container(AppProvider())
    setup_dishka(container, broker)

    @broker.on_event(TaskiqEvents.WORKER_STARTUP)  # pyright: ignore[reportArgumentType]
    async def init_container(_: dict[str, object]):
        await container.__aenter__()

    @broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)  # pyright: ignore[reportArgumentType]
    async def close_container(_: dict[str, object]):
        await container.close()

    @broker.task()
    @inject(patch_module=True)
    async def handle(resource: FromDishka[Resource]):
        received.append(resource.value)

    assert get_container(broker) is container
    assert get_dispatch_container(broker) is container
    assert events == []

    await broker.startup()

    assert events == ["initialized"]
    await handle.kiq()  # pyright: ignore[reportCallIssue]
    assert received == ["resource"]

    await broker.shutdown()

    assert events == ["initialized", "closed"]
