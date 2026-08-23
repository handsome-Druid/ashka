# Bootstrap Lifecycle

`ashka` adds an application bootstrap phase to dishka containers. Dependencies
registered with `AshkaScope.BOOTSTRAP` retain dishka's `Scope.RUNTIME` lifetime,
but are resolved eagerly when the root container is initialized.

## Registering Bootstrap Dependencies

Use `ashka.provide` with `AshkaScope.BOOTSTRAP`:

```python
from collections.abc import Iterator

from ashka import AshkaScope, make_container, provide
from dishka import Provider


class Database:
    def connect(self) -> None:
        ...

    def close(self) -> None:
        ...


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    def database(self) -> Iterator[Database]:
        database = Database()
        database.connect()
        yield database
        database.close()


container = make_container(ApplicationProvider())
```

`make_container()` only registers bootstrap dependencies when it creates the
container. It does not run ashka's lifecycle `container.init()` or resolve
those dependencies. The user must explicitly call `container.init()` or
explicitly enter the container context to initialize the database. Once
initialized, the database remains cached for the runtime lifetime of that
container.

## Explicit Initialization

When not using the container context manager, `init()` must be called
explicitly:

```python
container.init()
...
container.close()
```

The asynchronous equivalent uses `make_async_container` and awaits both
lifecycle operations:

```python
from collections.abc import AsyncIterator

from ashka import AshkaScope, make_async_container, provide
from dishka import Provider


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    async def database(self) -> AsyncIterator[Database]:
        database = Database()
        database.connect()
        yield database
        database.close()


container = make_async_container(ApplicationProvider())

await container.init()
...
await container.close()
```

## Initialization Order

Synchronous containers initialize bootstrap dependencies sequentially in their
registration order. Each dependency finishes initialization before the next
one starts.

Asynchronous containers initialize bootstrap dependencies concurrently with
`asyncio.gather`. Their initialization order is therefore not sequential and
must not be relied upon. Express dependencies between bootstrap resources
through provider parameters instead of relying on registration order.

## Initialization Failure

If `init()` fails, neither the synchronous nor the asynchronous container
automatically cleans up initialized resources or closes itself. Resource
cleanup and container shutdown after initialization failure are the caller's
responsibility.

## Context-Managed Initialization

Entering the root container also initializes bootstrap dependencies. Exiting
the context closes the container and releases generator-based resources:

```python
with make_container(ApplicationProvider()) as container:
    ...
```

For asynchronous applications:

```python
async with make_async_container(ApplicationProvider()) as container:
    ...
```

## Runtime Dependencies

Only providers declared with `AshkaScope.BOOTSTRAP` are resolved during
initialization. Regular `Scope.RUNTIME` providers remain lazy and are created
when first requested:

```python
from dishka import Scope


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    def database(self) -> Database:
        return Database()

    @provide(scope=Scope.RUNTIME)
    def metrics(self) -> Metrics:
        return Metrics()
```

After `container.init()`, `Database` is available from the runtime cache while
`Metrics` is still created on its first `container.get(Metrics)` call.

## Container Compatibility

Importing `ashka` patches dishka's `Container`, `AsyncContainer`,
`make_container`, and `make_async_container` globally. Import `ashka` before
importing or storing references to those dishka APIs. Importing dishka first
emits a warning because previously stored references may bypass ashka's
behavior.

`ContainerType` and `AsyncContainerType` describe the additional ashka methods
for static type checkers. The factories return patched dishka container
instances rather than instances of these facade classes, so do not use
`isinstance(container, ContainerType)` or
`isinstance(container, AsyncContainerType)` as a runtime check.

Bootstrap sources and the bootstrap keys associated with each container are
stored in process-wide registries. Container closing uses dishka's `close()`
behavior and clears the container cache, so applications can create multiple
root containers but must close every container that is no longer used.

Containers must be created with ashka's patched `make_container` or
`make_async_container` factory to receive bootstrap registration. A container
created through an unpatched dishka factory can still be attached to an
integration, but it does not gain ashka's bootstrap dependency registration.

Repeated or concurrent calls to `init()` are not coordinated. Initialization
cancellation and partial failure are also not rolled back automatically. The
application must serialize initialization, call it once per container, and
clean up any partially initialized resources before closing the container.

## FastAPI Lifespan

FastAPI's lifespan is a natural place to bind container startup and shutdown:

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from ashka import make_async_container
from ashka.integrations.fastapi import get_container, setup_dishka
from dishka import Provider
from fastapi import FastAPI


container = make_async_container(ApplicationProvider())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app_container = get_container(app)
    await app_container.init()
    yield
    await app_container.close()


app = FastAPI(lifespan=lifespan)
setup_dishka(container, app)
```