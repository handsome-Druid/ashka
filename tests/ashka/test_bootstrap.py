from collections.abc import AsyncIterator, Iterator
from typing import Protocol, runtime_checkable

from ashka import BOOTSTRAP, provide  # pyright: ignore[reportUnknownVariableType]

import pytest
from dishka import Provider, Scope, make_async_container, make_container


class SyncResource:
    def __init__(self):
        self.closed = False


class AsyncResource:
    def __init__(self):
        self.closed = False


@runtime_checkable
class Initializable(Protocol):
    def init(self) -> None: ...


@runtime_checkable
class AsyncInitializable(Protocol):
    async def init(self) -> None: ...


@pytest.mark.parametrize("entrypoint", ["init", "context"])
def test_sync_bootstrap(entrypoint: str):
    calls: list[str] = []
    resource = SyncResource()

    class AppProvider(Provider):
        component = "app"

        @provide(scope=BOOTSTRAP)
        def resource(self) -> Iterator[SyncResource]:
            calls.append("bootstrap")
            yield resource
            resource.closed = True

        @provide(scope=Scope.RUNTIME)
        def runtime_value(self) -> int:
            calls.append("runtime")
            return 1

        @provide(scope=Scope.REQUEST)
        def request_value(self) -> str:
            return "request"

    container = make_container(AppProvider())
    assert calls == []

    def assert_initialized():
        assert calls == ["bootstrap"]
        assert container.get(SyncResource, component="app") is resource
        assert calls == ["bootstrap"]

        with container(scope=Scope.REQUEST) as request_container:
            assert request_container.get(str, component="app") == "request"

        assert calls == ["bootstrap"]
        assert container.get(int, component="app") == 1
        assert calls == ["bootstrap", "runtime"]

    if entrypoint == "init":
        assert isinstance(container, Initializable)
        container.init()
        assert_initialized()
        container.close()
    else:
        with container as entered:
            assert entered is container
            assert_initialized()

    assert resource.closed


@pytest.mark.asyncio
@pytest.mark.parametrize("entrypoint", ["init", "context"])
async def test_async_bootstrap(entrypoint: str):
    calls: list[str] = []
    resource = AsyncResource()

    class AppProvider(Provider):
        component = "app"

        @provide(scope=BOOTSTRAP)
        async def resource(self) -> AsyncIterator[AsyncResource]:
            calls.append("bootstrap")
            yield resource
            resource.closed = True

        @provide(scope=Scope.RUNTIME)
        async def runtime_value(self) -> int:
            calls.append("runtime")
            return 1

        @provide(scope=Scope.REQUEST)
        async def request_value(self) -> str:
            return "request"

    container = make_async_container(AppProvider())
    assert calls == []

    async def assert_initialized():
        assert calls == ["bootstrap"]
        assert await container.get(AsyncResource, component="app") is resource
        assert calls == ["bootstrap"]

        async with container(scope=Scope.REQUEST) as request_container:
            assert await request_container.get(str, component="app") == "request"

        assert calls == ["bootstrap"]
        assert await container.get(int, component="app") == 1
        assert calls == ["bootstrap", "runtime"]

    if entrypoint == "init":
        assert isinstance(container, AsyncInitializable)
        await container.init()
        await assert_initialized()
        await container.close()
    else:
        async with container as entered:
            assert entered is container
            await assert_initialized()

    assert resource.closed


def test_bootstrap_provide_direct_call():
    def create_value() -> int:
        return 1

    class AppProvider(Provider):
        value = provide(staticmethod(create_value), scope=BOOTSTRAP)

    container = make_container(AppProvider())
    assert isinstance(container, Initializable)
    container.init()
    assert container.get(int) == 1
    container.close()
