from collections.abc import AsyncIterator

from ashka_lifecycle import (
    AshkaScope,
    provide,  # pyright: ignore[reportUnknownVariableType]
)

from ashka.integrations import get_container as get_dispatch_container
from ashka.integrations.litestar import get_container, setup_dishka
from dishka import AsyncContainer, Provider, make_async_container
from litestar import Litestar, get
from litestar.testing import TestClient


def test_litestar_bootstrap_lifecycle():
    events: list[str] = []

    class Resource:
        value = "resource"

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        async def resource(self) -> AsyncIterator[Resource]:
            events.append("initialized")
            yield Resource()
            events.append("closed")

    container: AsyncContainer = make_async_container(AppProvider())

    async def init_container():
        await container.__aenter__()

    async def close_container():
        await container.close()

    @get("/")
    async def handle() -> str:
        return (await get_container(app).get(Resource)).value  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportGeneralTypeIssues]

    app = Litestar(
        route_handlers=[handle],
        on_startup=[init_container],
        on_shutdown=[close_container],
    )
    setup_dishka(container, app)

    assert get_container(app) is container
    assert get_dispatch_container(app) is container
    assert events == []

    with TestClient(app) as client:
        assert events == ["initialized"]
        assert client.get("/").text == "resource"

    assert events == ["initialized", "closed"]
