# ashka

[![CI](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml)
[![Publish](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml)

`ashka` extends `reagento/dishka` with application lifecycle support.

## Current Features

- Pass `BOOTSTRAP` to the `scope` parameter of `ashka.provide`, for example
	`@ashka.provide(scope=ashka.BOOTSTRAP)`, to register a dependency in the RUNTIME scope
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

See [FastStream support](FASTSTREAM.md) for its support status and manual opt-in.
