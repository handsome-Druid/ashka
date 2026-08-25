from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from ashka.integrations import get_container as get_dispatch_container
from ashka.integrations.starlette import get_container, setup_dishka
from dishka import Provider
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from ashka_lifecycle import (
    make_async_container,
    provide,  # pyright: ignore[reportUnknownVariableType]
)
from ashka_lifecycle.entities.scope import AshkaScope


def test_starlette_bootstrap_lifecycle():
    events: list[str] = []

    class Resource:
        value = "resource"

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        async def resource(self) -> AsyncIterator[Resource]:
            events.append("initialized")
            yield Resource()
            events.append("closed")

    container = make_async_container(AppProvider())

    @asynccontextmanager
    async def lifespan(_: Starlette):
        await container.init()
        yield
        await container.close()

    async def handle(_: object) -> PlainTextResponse:
        return PlainTextResponse((await get_container(app).get(Resource)).value)  # pyright: ignore[reportUnknownMemberType, reportGeneralTypeIssues]

    app = Starlette(routes=[Route("/", handle)], lifespan=lifespan)
    setup_dishka(container, app)

    assert get_container(app) is container
    assert get_dispatch_container(app) is container
    assert events == []

    with TestClient(app) as client:
        assert events == ["initialized"]
        assert client.get("/").text == "resource"  # pyright: ignore[reportUnknownMemberType]

    assert events == ["initialized", "closed"]
