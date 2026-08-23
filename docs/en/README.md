# ashka

## Requirements

See [pyproject.toml](../../pyproject.toml).

## Public API

### Monkey-Patched dishka APIs

Import `ashka` before importing these dishka APIs. With the correct import
order, ashka automatically replaces or extends the corresponding dishka APIs:

- `dishka.**.make_container` -> `ashka.**.make_container`
- `dishka.**.make_async_container` -> `ashka.**.make_async_container`
- `dishka.integrations.*.setup_dishka` -> `ashka.integrations.*.setup_dishka`

Prefer importing these APIs from `ashka` to avoid cases where the monkey patch
has not taken effect and to receive the correct return types.

FastStream is not enabled by importing `ashka`. Explicitly importing
`ashka.integrations.faststream` patches
`dishka.integrations.faststream.setup_dishka` and its version-specific
implementation.

### APIs That Must Be Imported From ashka

These APIs are not monkey-patched into dishka:

- `ashka.AshkaScope`
- `ashka.provide`
- `ashka.integrations.setup_dishka`
- `ashka.integrations.get_container`
- Each supported `ashka.integrations.<framework>.get_container`

`ashka.container.ContainerType` and
`ashka.async_container.AsyncContainerType` are not guaranteed public APIs.
They may only be used for type annotations, not runtime checks.
`isinstance(container, ContainerType)`,
`isinstance(container, AsyncContainerType)`,
`issubclass(type(container), ContainerType)`, and
`issubclass(type(container), AsyncContainerType)` always return `False` for
actual containers.

## Features

- [Bootstrap Lifecycle](features/bootstrap-lifecycle.md)
- [Integration Container Access](features/integration-container-access.md)
- [Type-Dispatched Integrations](features/type-dispatched-integrations.md)

## Support

- [FastStream Support](support/faststream.md)