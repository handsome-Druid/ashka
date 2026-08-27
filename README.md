# ashka

[![CI](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml)
[![Publish](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml)
[![Update dishka](https://github.com/handsome-Druid/ashka/actions/workflows/update-dishka.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/update-dishka.yml)

`ashka` extends `reagento/dishka` with async/sync application lifecycle support.

The `a` prefix lets `ashka` sort before `dishka`, helping ensure the correct
import order.

## Application Lifecycle

This feature requires the `ashka[lifecycle]` extra.

Declare the resources that must be ready before the application starts doing
work. Ashka initializes them with the application. During runtime, they follow
dishka's APP-scope behavior. When the container closes, dishka closes
generator-based resources:

```python
from collections.abc import AsyncIterator

import ashka
from ashka import AshkaScope, async_lifespan, provide
from dishka import Provider, make_async_container
from fastapi import FastAPI


class Database:
    async def connect(self) -> None: ...

    async def close(self) -> None: ...


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    async def database(self) -> AsyncIterator[Database]:
        database = Database()
        await database.connect()
        yield database
        await database.close()


app = FastAPI(lifespan=async_lifespan)
container = make_async_container(ApplicationProvider())

ashka.integrations.setup_dishka(container, app)
```

- **Startup:** Bootstrap dependencies are initialized before the application
  starts doing work.
- **Runtime:** Dependencies retain dishka's APP-scope caching and dependency
  behavior.
- **Shutdown:** Dishka closes generator-based resources with the container.

Independent asynchronous Bootstrap dependencies initialize concurrently.
When initialization order matters, express it through provider parameters.

## Container Access

This feature is available in the base `ashka` package and does not require the
`lifecycle` extra.

Attach a container through the central integration entry point, then retrieve
the same container wherever the framework object is available:

```python
import ashka
from dishka import make_async_container
from fastapi import FastAPI


app = FastAPI()
container = make_async_container()

ashka.integrations.setup_dishka(container, app)

assert ashka.integrations.get_container(app) is container
```

The central entry points dispatch to the corresponding integration from the
runtime type of the framework object.

## Documentation

- [English](https://github.com/handsome-Druid/ashka/blob/master/docs/en/README.md)
- [中文](https://github.com/handsome-Druid/ashka/blob/master/docs/zh/README.md)
