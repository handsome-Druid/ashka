# Integration Container Access

Each `ashka.integrations` module provides a `get_container` function alongside
its `setup_dishka` function. This gives application lifecycle code a consistent
way to retrieve the exact container previously attached to a framework object.

## Basic Pattern

Import both functions from the integration for the framework:

```python
from ashka.integrations.fastapi import get_container, setup_dishka
from dishka import make_async_container
from fastapi import FastAPI


app = FastAPI()
container = make_async_container(ApplicationProvider())

setup_dishka(container, app)

assert get_container(app) is container
```

`get_container` returns the same container passed to `setup_dishka`; it does
not create a second container. The framework object passed to `setup_dishka`
must also be passed to `get_container`.

## FastAPI Production Lifecycle

The retrieved container can be used from FastAPI's lifespan without keeping a
second application-global reference:

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from ashka.integrations.fastapi import get_container, setup_dishka
from dishka import make_async_container
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    container = get_container(app)
    await container.init()
    try:
        yield
    finally:
        await container.close()


app = FastAPI(lifespan=lifespan)
setup_dishka(make_async_container(ApplicationProvider()), app)
```

Application hooks, extensions, and infrastructure code can call
`get_container(app)` whenever they already receive the framework object.

## Celery Production Setup

Synchronous integrations use the same setup-and-retrieve pattern:

```python
from ashka.integrations.celery import get_container, setup_dishka
from celery import Celery
from dishka import make_container


app = Celery("worker")
container = make_container(ApplicationProvider())

setup_dishka(container, app)
get_container(app).init()
```

Worker shutdown code can retrieve and close the same container:

```python
get_container(app).close()
```

## Framework-Specific Setup Arguments

Integration modules preserve the setup signature and behavior supplied by the
corresponding dishka integration. Additional positional and keyword arguments
can be passed through `setup_dishka` when required by that framework:

```python
setup_dishka(container, app, auto_inject=True)
```

The exact optional arguments are defined by the selected dishka integration.

## Lifecycle and Setup Requirements

Call `setup_dishka` successfully before calling `get_container`. An integration
stores the container in its framework-specific location, so calling
`get_container` before setup may raise that framework's native `AttributeError`
or `KeyError` rather than a common ashka exception.

`get_container` only retrieves the stored reference. It does not initialize or
close the container and does not assume ownership of its lifecycle. The
application remains responsible for pairing `init()` with `close()` or using a
container context manager.

Calling setup more than once may replace the stored container reference. It
does not close the previously attached container, so close the old container
before replacing it.

## Integration Constraints

Framework packages such as FastAPI, Celery, and Litestar are optional
development dependencies and are not installed with ashka. Install the
frameworks and dishka integrations required by the application explicitly.

Most optional framework dependencies do not have an upper version bound.
Verify the selected framework and dishka versions together before deployment.

Optional integrations are enabled during import by checking whether their
framework package is available. An `ImportError` raised while loading an
installed integration can also leave that integration unavailable, so verify
the central setup entry point during application startup.