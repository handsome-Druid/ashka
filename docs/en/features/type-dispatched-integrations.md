# Type-Dispatched Integrations

The central `ashka.integrations` entry points select an integration from the
runtime type of the framework object. They provide one import path for setup
and container access across supported frameworks.

## Central Entry Points

Import `ashka`, then use `setup_dishka` and `get_container` through `ashka.integrations`:

```python
import ashka
```

Both functions accept the framework object used by its integration. Setup uses
the common container-first call shape:

```python
ashka.integrations.setup_dishka(container, app)
container = ashka.integrations.get_container(app)
```

The framework object's runtime type determines which registered integration is
called.

## Framework-Independent Setup

Infrastructure code can retrieve a container and manage its lifecycle without
importing a framework-specific ashka module:

```python
import ashka
from dishka import AsyncContainer, Container


container = ashka.integrations.get_container(app)

if isinstance(container, AsyncContainer):
    await container.init()
    ...
    await container.close()
elif isinstance(container, Container):
    container.init()
    ...
    container.close()
```

The runtime check uses the actual dishka container classes. The second argument
to `isinstance` must be `dishka.Container` or `dishka.AsyncContainer`, not
ashka's annotation-only `ashka.container.ContainerType` or
`ashka.async_container.AsyncContainerType`; checks against the latter two
always return `False` for actual containers.

The same central functions cover Aiogram, Aiohttp, ARQ, Celery, Click,
FastAPI, Flask, Litestar, Sanic, Starlette, Taskiq, and Telebot.

## Application Subclasses

Dispatch follows the application's class hierarchy, so framework subclasses use
the registration of their base framework class:

```python
import ashka
from fastapi import FastAPI


class Application(FastAPI):
    pass


app = Application()
container = ashka.make_async_container(ApplicationProvider())

ashka.integrations.setup_dishka(
    container, app
)  # Equivalent to ashka.integrations.fastapi.setup_dishka(container, app)
container = ashka.integrations.get_container(
    app
)  # Equivalent to ashka.integrations.fastapi.get_container(app)
```

This allows projects to use their own application subclasses without adding a
second dispatch registration.

## Passing Integration Options

Additional arguments are forwarded to the selected integration:

```python
ashka.integrations.setup_dishka(container, app, auto_inject=True)
```

This keeps framework-specific setup options available while retaining the
central entry point.

## Unsupported Application Types

If no integration is registered for an object's type, the central function
raises `TypeError` and identifies that type:

```python
import ashka


class UnsupportedApplication:
    pass


ashka.integrations.get_container(UnsupportedApplication())
```

This makes missing integration registration visible at application setup time.

## Dispatch Constraints

Dispatch uses only the framework object's runtime type. It does not validate
whether the supplied container is synchronous or asynchronous, whether it was
created by ashka, or whether it matches the selected framework integration.

Importing `ashka` imports the default integration modules and installs their
registrations. Available registrations depend on installed optional
dependencies.

ARQ dispatch is registered for `dict`, because an ARQ worker context is a
dictionary. As a result, any dictionary passed to the central entry points is
treated as an ARQ context.

FastStream is not imported or registered by the central integration module.
Applications opting into FastStream support must import
`ashka.integrations.faststream` explicitly and follow the separate FastStream
support guidance.

Calling setup again for the same application object can overwrite its stored
container reference without closing the old container. The application must
manage replacement and shutdown explicitly.