from collections.abc import Generator
from threading import Lock

from ashka import (
    AshkaScope,
    async_lifespan,
    provide,  # pyright: ignore[reportUnknownVariableType]
)
from ashka.integrations import setup_dishka

from dishka import (
    AsyncContainer,
    Container,
    Provider,
    make_async_container,
    make_container,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import LogCaptureFixture, fixture

result = 0
lock = Lock()


class P(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    @staticmethod
    def _() -> Generator[None, None, None]:
        global result
        result = 1
        yield
        result = 0


@fixture
def async_container():
    return make_async_container(P())


@fixture
def container():
    return make_container(P())


def test_async_lifespan(async_container: AsyncContainer):
    app = FastAPI(lifespan=async_lifespan)
    setup_dishka(async_container, app)
    test_client = TestClient(app)
    assert result == 0
    with lock:
        with test_client:
            assert result == 1
        assert result == 0


def test_async_lifespan_with_sync_container(
    container: Container, caplog: LogCaptureFixture
):
    app = FastAPI(lifespan=async_lifespan)
    setup_dishka(container, app)
    test_client = TestClient(app)
    assert result == 0
    with lock:
        caplog.clear()
        with test_client:
            assert result == 1
            assert "Should not" in caplog.text
            caplog.clear()
        assert result == 0
