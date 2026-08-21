# ashka

[![CI](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml)
[![Publish](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml/badge.svg)](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml)

## Dishka Patched Implementations

- `dishka.integrations.*.setup_dishka` -> `ashka.integrations.*.setup_dishka`

## Disable Import Warning

To disable the warning about importing `dishka` before `ashka`, set this environment variable to `1`, `true`, `yes`, or `on` before importing the package:

```text
ASHKA_DISABLE_IMPORT_WARNING=1
```
