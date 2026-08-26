from collections.abc import Generator

from ashka_lifecycle import AshkaScope, provide

from dishka import (
    AsyncContainer,
    Container,
    Provider,
    Scope,
    make_async_container,
    make_container,
)
from pytest import fixture, mark

result = 0


def func() -> Generator[None, None, None]:
    global result
    result += 1
    yield
    result -= 1


class P(Provider):
    bootstrap = provide(staticmethod(func), scope=AshkaScope.BOOTSTRAP)
    runtime = provide(staticmethod(func), scope=Scope.RUNTIME)
    app = provide(staticmethod(func), scope=Scope.APP)


@fixture
def container():
    return make_container(P())


@fixture
def async_container():
    return make_async_container(P())


@mark.asyncio
async def test_provide_mutiple_times(
    container: Container, async_container: AsyncContainer
):
    assert result == 0
    with container:
        assert result == 1
        async with async_container:
            assert result == 2
        assert result == 1
    assert result == 0
