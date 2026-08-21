# ashka

[![CI](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml)
[![Publish](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml)

## Dishka Patched Implementations

- `dishka.integrations.aiohttp.setup_dishka` -> `ashka.integrations.aiohttp.setup_dishka`
- `dishka.integrations.fastapi.setup_dishka` -> `ashka.integrations.fastapi.setup_dishka`
- `dishka.integrations.starlette.setup_dishka` -> `ashka.integrations.starlette.setup_dishka`
- `dishka.integrations.litestar.setup_dishka` -> `ashka.integrations.litestar.setup_dishka`
- `dishka.integrations.flask.setup_dishka` -> `ashka.integrations.flask.setup_dishka`
- `dishka.integrations.sanic.setup_dishka` -> `ashka.integrations.sanic.setup_dishka`

## Disable Import Warning

To disable the warning about importing `dishka` before `ashka`, set this environment variable to `1`, `true`, `yes`, or `on` before importing the package:

```text
ASHKA_DISABLE_IMPORT_WARNING=1
```
