# FastStream Support

> [!WARNING]
> This integration is provided without any guarantee of availability,
> compatibility, or correctness. Do not use it in a production environment
> unless it has been thoroughly tested against the exact dependency versions
> and application configuration being deployed.

FastStream support is not enabled during `ashka` initialization.

It is also excluded from the project's regular coverage target and is not
registered by the central `ashka.integrations` import.

## Upstream Deprecation

The upstream `dishka.integrations.faststream` interface is deprecated and has
been moved to the separately maintained `dishka-faststream` package.

## Version Testing

FastStream requires version-specific integration code. FastStream 0.5, 0.6,
and 0.7 use different internal APIs, while optional integrations such as
`StreamRouter` depend on compatible FastStream and FastAPI versions. Official
support therefore requires a test matrix covering the supported combinations,
which is not currently available in this project.

The current implementation depends on private FastStream APIs. Those APIs can
change without a compatibility period, including between minor FastStream
releases.

Contributions providing the required version-specific tests are welcome. Once
the supported combinations are fully covered, FastStream can be included in the
supported integrations.

## Manual Import

The implementation remains available for explicit use, but it is not imported
automatically. Applications that need it can opt in manually:

```python
import ashka.integrations.faststream
```

If an error occurs during actual use, please open an issue and include the
relevant FastStream, FastAPI, and dishka versions. The maintainer will switch to
the affected version combination to reproduce and fix the problem.