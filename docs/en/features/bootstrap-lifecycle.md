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

from ashka import AshkaScope, make_container, provide
from dishka import Provider


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

### Bootstrap Dependency-Key Conflicts

ashka-lifecycle's patched `make_container()` and `make_async_container()`
check every BOOTSTRAP factory's component and provided type when they create a
container. This is ashka-lifecycle behavior, not behavior of the original
dishka factories. If two factories have the same component and type, container
creation raises `ValueError`.

This check is required because `init()` resolves each bootstrap dependency with
`get()` using its component and type. Two factories with the same dependency
key would make the resolved factory ambiguous. To ensure every BOOTSTRAP
factory can be initialized successfully, ashka-lifecycle does not allow such
duplicates.

The simplest ways to avoid a conflict are to use different components, return
a `Literal` or `NewType`, or use `provides` to assign a different provided
type:

```python
from typing import Literal, NewType


class FirstProvider(Provider):
    component = "first"

    @provide(scope=AshkaScope.BOOTSTRAP)
    def resource(self) -> None: ...


class SecondProvider(Provider):
    component = "second"

    @provide(scope=AshkaScope.BOOTSTRAP)
    def resource(self) -> None: ...


class TypedProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    def literal_resource(self) -> Literal["resource"]: ...

    @provide(
        scope=AshkaScope.BOOTSTRAP,
        provides=NewType("ResourceName", str),
    )
    def named_resource(self): ...
```

Do not set the `scope` attribute of a native dishka `Provider` directly to
`AshkaScope.BOOTSTRAP`. This usage is not allowed and is not currently planned
to be supported.

`make_container()` only registers bootstrap dependencies when it creates the
container. It does not run ashka's lifecycle `container.init()` or resolve
those dependencies. The user must explicitly call `container.init()` or
explicitly enter the container context to initialize the database. Once
initialized, the database remains cached for the app lifetime of that
container.

## Explicit Initialization

When not using the container context manager, `init()` must be called
explicitly:

```python
container.init()
...
container.close()
```

If a test repeatedly creates containers and should also remove ashka's reference
to a container after closing it, import
`ashka.entities.bootstrap.bootstrap_keys_by_container` and remove the
corresponding key:

```python
from ashka.entities.bootstrap import bootstrap_keys_by_container

bootstrap_keys_by_container.pop(container, None)
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

Importing `ashka` patches dishka's `Container`, `AsyncContainer`,
`make_container`, and `make_async_container` globally. Import `ashka` before
importing or storing references to those dishka APIs. Importing dishka first
emits a warning because previously stored references may bypass ashka's
behavior.

These monkey patches keep the API paths consistent with upstream dishka and
reduce the cognitive load during migration. They exist for legacy-project
compatibility: importing `ashka` first lets an existing project keep its
current dishka imports without immediate code changes. This is a migration aid,
not a stable long-term usage pattern; migrate imports from dishka to ashka
incrementally when convenient instead of relying on the monkey patches
indefinitely.

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