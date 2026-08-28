# ashka

## Requirements

See [pyproject.toml](../../pyproject.toml).

## Installation

Install `ashka[lifecycle]` to enable all features, including Bootstrap
lifecycle support, `AshkaScope.BOOTSTRAP`, and explicit or context-managed
container initialization. This installation adds `init()` to dishka's
synchronous and asynchronous containers and extends context entry so that
dependencies can be initialized during the Bootstrap phase.

If Bootstrap lifecycle support is not needed, install `ashka` without the
extra. This provides supported framework integrations, unified container
access, and type-dispatched integration setup, but does not provide the
Bootstrap lifecycle APIs. Importing `ashka` replaces `setup_dishka` in some
Dishka framework integrations so existing Dishka import paths can use
ashka's extended integration behavior.

## Public API

Prefer importing the APIs below from `ashka` to receive the correct return
types. Some dishka APIs are monkey-patched for legacy-project compatibility;
import `ashka` before using them. This is a migration aid, so migrate dishka
imports to ashka instead of relying on the monkey patches long term.

| API | Notes |
| --- | --- |
| `dishka.integrations.*.setup_dishka` | Is monkey-patched |
| `ashka.activate` | Must be imported from `ashka` |
| `ashka.integrations.setup_dishka` | Must be imported from `ashka` |
| `ashka.integrations.get_container` | Must be imported from `ashka` |
| `ashka.integrations.<framework>.get_container` | Must be imported from `ashka` |
| `ashka.integrations.faststream.setup_dishka` | Must be imported from `ashka.integrations.faststream`; importing it applies the monkey patch |
| `ashka.integrations.faststream.get_container` | Must be imported from `ashka.integrations.faststream` |
| `ashka.lifespan` | Must be imported from `ashka`; installing `ashka[lifecycle]` automatically attaches `container.init()` to the lifespan |
| `ashka.async_lifespan` | Must be imported from `ashka`; installing `ashka[lifecycle]` automatically attaches `container.init()` to the lifespan |
| `dishka.provide` | Is monkey-patched; requires `ashka[lifecycle]` |
| `dishka.Container.init` | Is added by monkey patch; requires `ashka[lifecycle]` |
| `dishka.AsyncContainer.init` | Is added by monkey patch; requires `ashka[lifecycle]` |
| `ashka.AshkaScope` | Must be imported from `ashka`; requires `ashka[lifecycle]` |

`ashka.container.ContainerType` and
`ashka.async_container.AsyncContainerType` are not guaranteed public APIs.
They may only be used for type annotations, not runtime checks.
`isinstance(container, ContainerType)`,
`isinstance(container, AsyncContainerType)`,
`issubclass(type(container), ContainerType)`, and
`issubclass(type(container), AsyncContainerType)` always return `False` for
actual containers.

## Features

- [Use activate to Defeat Lazy Imports](features/activate.md)
- [Integration Container Access](features/integration-container-access.md)
- [Type-Dispatched Integrations](features/type-dispatched-integrations.md)
- [Bootstrap Lifecycle](features/bootstrap-lifecycle.md) (requires `ashka[lifecycle]`)
- [Generic Lifespan](features/lifespan.md)

## Support

- [FastStream Support](support/faststream.md)