# ashka

## Dishka Patched Implementations

- `dishka.integrations.fastapi.setup_dishka` -> `ashka.integrations.fastapi.setup_dishka`
- `dishka.integrations.flask.setup_dishka` -> `ashka.integrations.flask.setup_dishka`
- `dishka.integrations.sanic.setup_dishka` -> `ashka.integrations.sanic.setup_dishka`

## Disable Import Warning

To disable the warning about importing `dishka` before `ashka`, set this environment variable to `1`, `true`, `yes`, or `on` before importing the package:

```text
ASHKA_DISABLE_IMPORT_WARNING=1
```
