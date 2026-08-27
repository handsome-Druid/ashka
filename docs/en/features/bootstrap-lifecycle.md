# Bootstrap Lifecycle

This feature requires the `ashka[lifecycle]` extra.

`ashka` adds an application bootstrap phase to dishka containers. Dependencies
registered with `AshkaScope.BOOTSTRAP` use dishka's `Scope.APP` lifetime,
but are resolved eagerly when the root container is initialized.

In dishka's scope hierarchy, `Scope.RUNTIME` is the outer scope of
`Scope.APP`, while `Scope.APP` is its inner scope. A `Scope.APP` factory can
therefore depend on a `Scope.RUNTIME` factory, but the reverse dependency is
not allowed. `AshkaScope.BOOTSTRAP` is not a new dishka scope; it is an
ashka marker for eager resolution. ashka converts it to `Scope.APP`, so a
bootstrap factory follows APP scope's dependency, caching, and shutdown
behavior.

## Registering Bootstrap Dependencies

Use `ashka.provide` with `AshkaScope.BOOTSTRAP`:

```python
from collections.abc import Iterator

from ashka import AshkaScope, provide
from dishka import Provider, make_container


class Database:
    def connect(self) -> None: ...

    def close(self) -> None: ...


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    def database(self) -> Iterator[Database]:
        database = Database()
        database.connect()
        yield database
        database.close()


container = make_container(ApplicationProvider())
```

When dishka creates a provide factory, the factory's provided type must be
determined by its return annotation or the `provides` parameter. Therefore,
even a bootstrap factory that only performs initialization and has no meaningful
return value must explicitly declare `-> None`:

```python
class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    async def initialize(self) -> None: ...
```

For a factory that provides another type, use the `provides` parameter to set
the type explicitly instead.

Do not set the `scope` attribute of a native dishka `Provider` directly to
`AshkaScope.BOOTSTRAP`. This usage is not allowed and is not currently planned
to be supported.

`make_container()` only creates the container. It does not run ashka's
lifecycle `container.init()` or resolve bootstrap dependencies. When the user
calls `container.init()` or enters the container context, ashka scans the
container's registry and resolves the bootstrap dependencies found there.
Once initialized, the database remains cached for the app lifetime of that
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

from ashka import AshkaScope, provide
from dishka import Provider, make_async_container


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

`lock_factory` is configured when the asynchronous container is created, not
when `init()` is called. By default, dishka uses a lock that would serialize
container resolutions. To allow independent bootstrap resolutions to overlap,
pass `lock_factory=None` when creating the container:

```python
container = make_async_container(
    ApplicationProvider(),
    lock_factory=None,
)
```

This disables dishka's container lock. Use it only when concurrent container
access is safe.

## Initialization Order

Synchronous containers initialize bootstrap dependencies sequentially in their
registration order. Each dependency finishes initialization before the next
one starts.

Asynchronous containers request bootstrap dependencies concurrently with
`asyncio.gather`. The initialization order must not be relied upon. Express
dependencies between bootstrap resources through provider parameters instead
of relying on registration order.

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

## Bootstrap and Regular Scopes

Only factories registered with `AshkaScope.BOOTSTRAP` are resolved eagerly during
initialization. Factories registered directly with `Scope.APP` or
`Scope.RUNTIME` are not triggered automatically. `Scope.APP` and
`Scope.RUNTIME` are the regular factory scopes. When a factory is registered
with `AshkaScope.BOOTSTRAP`, ashka converts it to `Scope.APP` and resolves it
eagerly during initialization:

```python
from dishka import Scope


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    def database(self) -> Database:
        return Database()

    @provide(scope=Scope.APP)
    def cache(self) -> Cache:
        return Cache()

    @provide(scope=Scope.RUNTIME)
    def metrics(self) -> Metrics:
        return Metrics()
```

Neither the `cache` nor `metrics` factory is invoked by `container.init()` in this example;
each is created only when `container.get(Cache)` or `container.get(Metrics)` is
called for the first time. Only a factory registered with
`AshkaScope.BOOTSTRAP` is triggered automatically by `container.init()` or by
entering the root container. That factory uses `Scope.APP` lifetime and stays
cached in the APP scope.

## Container Compatibility

Importing `ashka` with the lifecycle extra patches dishka's `Container` and
`AsyncContainer` globally. The patches add `init()` and initialize bootstrap
dependencies when the container context is entered. `make_container` and
`make_async_container` remain dishka's native factories and can be imported
directly from `dishka`.

Import `ashka` before using the lifecycle methods so the container patches are
active.

`ContainerType` and `AsyncContainerType` describe the additional `init()`
methods for static type checkers. Dishka's native factories return patched
dishka container instances rather than instances of these facade classes, so
do not use `isinstance(container, ContainerType)` or
`isinstance(container, AsyncContainerType)` as a runtime check.

During initialization, ashka traverses the container's registry chain and
resolves the bootstrap dependency keys found in each registry. Container
closing uses dishka's `close()` behavior and clears the container cache, so
applications can create multiple root containers but must close every
container that is no longer used.

Repeated or concurrent calls to `init()` are not coordinated. Initialization
cancellation and partial failure are also not rolled back automatically. The
application must serialize initialization, call it once per container, and
clean up any partially initialized resources before closing the container.

## FastAPI Lifespan

FastAPI's lifespan is a natural place to bind container startup and shutdown:

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from ashka.integrations.fastapi import get_container, setup_dishka
from dishka import Provider, make_async_container
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