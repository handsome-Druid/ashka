from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Protocol, runtime_checkable

from ashka import BOOTSTRAP, provide  # pyright: ignore[reportUnknownVariableType]
from ashka.integrations.fastapi import get_container, setup_dishka

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import FastAPI
from fastapi.testclient import TestClient


@runtime_checkable
class Initializable(Protocol):
    async def init(self) -> None: ...


def test_fastapi_bootstrap_lifespan():
    events: list[str] = []

    class AppProvider(Provider):
        @provide(scope=BOOTSTRAP)
        async def resource(self) -> AsyncIterator[str]:
            events.append("initialized")
            yield "resource"
            events.append("closed")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        container = get_container(app)
        assert isinstance(container, AsyncContainer)
        assert isinstance(container, Initializable)
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
