# ashka

[![CI](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml)
[![Publish](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml)

`ashka` extends `reagento/dishka` with async/sync application lifecycle support.

The `a` prefix lets `ashka` sort before `dishka`, helping ensure the correct
import order. The name also means async application lifecycle support, which can
speed up startup compared with serially initializing components in a lifespan
function.

## Documentation

- [English](https://github.com/handsome-Druid/ashka/blob/master/docs/en/README.md)
- [中文](https://github.com/handsome-Druid/ashka/blob/master/docs/zh/README.md)

## Current Features

- Pass `AshkaScope.BOOTSTRAP` to the `scope` parameter of `ashka.provide`, for example
	`@ashka.provide(scope=ashka.AshkaScope.BOOTSTRAP)`, to register a dependency in the APP scope
	and create it when the container is initialized. Both synchronous and
	asynchronous containers can be initialized explicitly with `container.init()`
	or automatically by entering the container context manager.
- Each ashka integration provides a consistent `get_container` function. It
	retrieves the container passed to `setup_dishka` from the integrated
	framework application, router, broker, context, or other supported object.
- The central `ashka.integrations.setup_dishka` and
	`ashka.integrations.get_container` functions automatically dispatch to the
	corresponding integration based on the type of the object passed to them.
- Integrations are available for Aiogram, Aiohttp, ARQ, Celery, Click, FastAPI,
	Flask, Litestar, Sanic, Starlette, Taskiq, and Telebot. FastStream is
	available as a manual opt-in integration.

## Patched Implementations

- `dishka.**.make_container` -> `ashka.**.make_container`
- `dishka.**.make_async_container` -> `ashka.**.make_async_container`
- `dishka.integrations.*.setup_dishka` -> `ashka.integrations.*.setup_dishka`

These monkey patches keep the API paths consistent with upstream dishka and
reduce the cognitive load during migration. Import `ashka` before importing
these dishka APIs so existing projects can keep their current imports without
immediate code changes. This is a migration aid rather than a stable usage
pattern; migrate imports from dishka to ashka incrementally when convenient
instead of relying on the monkey patches indefinitely.

See [FastStream support](https://github.com/handsome-Druid/ashka/blob/master/docs/en/support/faststream.md) for its support status and manual opt-in.
