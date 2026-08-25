from collections.abc import Generator

from ashka import (
    AshkaScope,
    async_lifespan,
    make_async_container,
    provide,  # pyright: ignore[reportUnknownVariableType]
)
from ashka.integrations import setup_dishka

from dishka import AsyncContainer, Provider
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import fixture

result = 0


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


def test_async_lifespan(async_container: AsyncContainer):
    app = FastAPI(lifespan=async_lifespan)
    setup_dishka(async_container, app)
    test_client = TestClient(app)
    assert result == 0
    with test_client:
        assert result == 1
    assert result == 0
