from collections.abc import AsyncIterator

from ashka_lifecycle import (
    AshkaScope,
    provide,  # pyright: ignore[reportUnknownVariableType]
)

import pytest
from arq import Worker
from ashka.integrations import get_container as get_dispatch_container
from ashka.integrations.arq import get_container, setup_dishka
from dishka import AsyncContainer, Provider, make_async_container


@pytest.mark.asyncio
async def test_arq_bootstrap_lifecycle():
    events: list[str] = []

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        async def resource(self) -> AsyncIterator[str]:
            events.append("initialized")
            yield "resource"
            events.append("closed")

    async def job(ctx: dict[str, object]): ...
    async def init_container(ctx: dict[str, object]):
        await container.__aenter__()

    async def close_container(ctx: dict[str, object]):
        await container.close()

    container: AsyncContainer = make_async_container(AppProvider())
    worker = Worker(
        [job],
        handle_signals=False,
        on_startup=init_container,
        on_shutdown=close_container,
    )
    setup_dishka(container, worker)

    assert get_container(worker) is container
    assert get_dispatch_container(worker) is container
    assert events == []

    assert worker.on_startup is not None
    await worker.on_startup(worker.ctx)

    assert events == ["initialized"]

    assert worker.on_job_start is not None
    await worker.on_job_start(worker.ctx)
    assert worker.on_job_end is not None
    await worker.on_job_end(worker.ctx)
    assert worker.on_shutdown is not None
    await worker.on_shutdown(worker.ctx)

    assert events == ["initialized", "closed"]
