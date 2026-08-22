# ashka

[![CI](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml)
[![Publish](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml)

`ashka` is an add-ons library for `reagento/dishka`.

## Current Features

- Each ashka integration provides a consistent `get_container` function. It
	retrieves the container passed to `setup_dishka` from the integrated
	framework application, router, broker, context, or other supported object.
- The central `ashka.integrations.setup_dishka` and
	`ashka.integrations.get_container` functions automatically dispatch to the
	corresponding integration based on the type of the object passed to them.

## Patched Implementations

- `dishka.integrations.*.setup_dishka` -> `ashka.integrations.*.setup_dishka`

See [FastStream support](FASTSTREAM.md) for its support status and manual opt-in.
