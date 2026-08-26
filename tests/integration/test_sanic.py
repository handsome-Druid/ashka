from collections.abc import AsyncIterator

from ashka_lifecycle import (
    make_async_container,
    provide,  # pyright: ignore[reportUnknownVariableType]
)
from ashka_lifecycle.entities.scope import AshkaScope

from ashka.integrations import get_container as get_dispatch_container
from ashka.integrations.sanic import get_container, setup_dishka
from dishka import FromDishka, Provider
from sanic import Sanic, text


def test_sanic_bootstrap_lifecycle():
    events: list[str] = []
    running_events: list[str] = []

    class Resource:
        value = "resource"

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        async def resource(self) -> AsyncIterator[Resource]:
            events.append("initialized")
            yield Resource()
            events.append("closed")

    app = Sanic("test_sanic")
    container = make_async_container(AppProvider())

    @app.before_server_start
    async def init_container(*_: object):
        await container.init()

    @app.after_server_stop
    async def close_container(*_: object):
        await container.close()

    @app.get("/")
    async def handle(_: object, resource: FromDishka[Resource]):
        running_events.extend(events)
        return text(resource.value)

    setup_dishka(container, app, auto_inject=True)

    assert get_container(app) is container
    assert get_dispatch_container(app) is container
    assert events == []

    _, response = app.test_client.get("/")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType] # pyright: ignore[reportUnknownMemberType]

    assert response.text == "resource"  # pyright: ignore[reportUnknownMemberType]
    assert running_events == ["initialized"]
    assert events == ["initialized", "closed"]
