from collections.abc import AsyncIterator, Iterator

from ashka import (
    BOOTSTRAP,
    make_async_container,
    make_container,
    provide,  # pyright: ignore[reportUnknownVariableType]
)
from ashka.async_container import AsyncContainerType
from ashka.container import ContainerType

import pytest
from dishka import AsyncContainer, Container, Provider, Scope


class SyncResource:
    def __init__(self):
        self.closed = False


class AsyncResource:
    def __init__(self):
        self.closed = False


@pytest.mark.parametrize("scope", list(Scope))
def test_sync_container_in_each_scope(scope: Scope):
    injected_containers: list[Container] = []

    class AppProvider(Provider):
        @provide(scope=scope)
        def value(self, container: Container) -> str:
            injected_containers.append(container)
            return scope.name

    container = make_container(
        AppProvider(),
        start_scope=scope if scope in (Scope.RUNTIME, Scope.APP) else Scope.APP,
    )

    if scope in (Scope.RUNTIME, Scope.APP):
        assert container.scope is scope
        assert container.get(Container) is container
        assert container.get(str) == scope.name
        assert injected_containers == [container]
    else:
        with container(scope=scope) as scoped_container:
            assert scoped_container.scope is scope
            assert scoped_container.get(Container) is scoped_container
            assert scoped_container.get(str) == scope.name
            assert injected_containers == [scoped_container]

    container.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("scope", list(Scope))
async def test_async_container_in_each_scope(scope: Scope):
    injected_containers: list[AsyncContainer] = []

    class AppProvider(Provider):
        @provide(scope=scope)
        async def value(self, container: AsyncContainer) -> str:
            injected_containers.append(container)
            return scope.name

    container = make_async_container(
        AppProvider(),
        start_scope=scope if scope in (Scope.RUNTIME, Scope.APP) else Scope.APP,
    )

    if scope in (Scope.RUNTIME, Scope.APP):
        assert container.scope is scope
        assert await container.get(AsyncContainer) is container
        assert await container.get(str) == scope.name
        assert injected_containers == [container]
    else:
        async with container(scope=scope) as scoped_container:
            assert scoped_container.scope is scope
            assert await scoped_container.get(AsyncContainer) is scoped_container
            assert await scoped_container.get(str) == scope.name
            assert injected_containers == [scoped_container]

    await container.close()


@pytest.mark.parametrize("entrypoint", ["init", "context"])
def test_sync_bootstrap(entrypoint: str):
    calls: list[str] = []
    injected_containers: list[Container] = []
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
        def request_value(self, container: Container) -> str:
            injected_containers.append(container)
            return "request"

    container: ContainerType = make_container(AppProvider())
    assert isinstance(container, Container)
    assert calls == []

    def assert_initialized():
        assert calls == ["bootstrap"]
        assert container.get(Container) is container
        assert container.get(SyncResource, component="app") is resource
        assert calls == ["bootstrap"]

        with container(scope=Scope.REQUEST) as request_container:
            assert isinstance(request_container, Container)
            assert request_container.get(Container) is request_container
            assert request_container.get(str, component="app") == "request"
            assert injected_containers == [request_container]

        assert calls == ["bootstrap"]
        assert container.get(int, component="app") == 1
        assert calls == ["bootstrap", "runtime"]

    if entrypoint == "init":
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
    injected_containers: list[AsyncContainer] = []
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
        async def request_value(self, container: AsyncContainer) -> str:
            injected_containers.append(container)
            return "request"

    container: AsyncContainerType = make_async_container(AppProvider())
    assert isinstance(container, AsyncContainer)
    assert calls == []

    async def assert_initialized():
        assert calls == ["bootstrap"]
        assert await container.get(AsyncContainer) is container
        assert await container.get(AsyncResource, component="app") is resource
        assert calls == ["bootstrap"]

        async with container(scope=Scope.REQUEST) as request_container:
            assert isinstance(request_container, AsyncContainer)
            assert await request_container.get(AsyncContainer) is request_container
            assert await request_container.get(str, component="app") == "request"
            assert injected_containers == [request_container]

        assert calls == ["bootstrap"]
        assert await container.get(int, component="app") == 1
        assert calls == ["bootstrap", "runtime"]

    if entrypoint == "init":
        await container.init()
        await assert_initialized()
        await container.close()
    else:
        async with container as entered:
            assert entered is container
            await assert_initialized()

    assert resource.closed


def test_bootstrap_provide_direct_call():
    calls: list[str] = []

    def create_value() -> int:
        calls.append("bootstrap")
        return 1

    class AppProvider(Provider):
        value = provide(staticmethod(create_value), scope=BOOTSTRAP)

    container = make_container(AppProvider())
    assert isinstance(container, Container)
    assert calls == []
    container.init()
    assert calls == ["bootstrap"]
    assert container.get(int) == 1
    assert calls == ["bootstrap"]
    container.close()
