from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from ashka import (
    make_async_container,
    provide,  # pyright: ignore[reportUnknownVariableType]
)
from ashka.entities.scope import AshkaScope
from ashka.integrations.fastapi import get_container, setup_dishka

from dishka import AsyncContainer, Provider
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_fastapi_bootstrap_lifespan():
    events: list[str] = []

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        async def resource(self) -> AsyncIterator[str]:
            events.append("initialized")
            yield "resource"
            events.append("closed")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app_container = get_container(app)
        assert isinstance(app_container, AsyncContainer)
        assert app_container is container
        await container.init()
        yield
        await container.close()

    app = FastAPI(lifespan=lifespan)
    container = make_async_container(AppProvider())
    setup_dishka(container, app)

    assert app.state.dishka_container is container
    assert get_container(app) is container
    assert events == []

    with TestClient(app):
        assert get_container(app) is container
        assert events == ["initialized"]

    assert events == ["initialized", "closed"]
