# ashka-lifecycle

[![CI](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml/badge.svg?branch=lifecycle)](https://github.com/handsome-Druid/ashka/actions/workflows/ci.yml)
[![Publish](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml/badge.svg?branch=lifecycle)](https://github.com/handsome-Druid/ashka/actions/workflows/publish.yml)
[![Update dishka](https://github.com/handsome-Druid/ashka/actions/workflows/update-dishka.yml/badge.svg?branch=lifecycle)](https://github.com/handsome-Druid/ashka/actions/workflows/update-dishka.yml)

`ashka-lifecycle` adds an application bootstrap phase to dishka containers. Dependencies
registered with `AshkaScope.BOOTSTRAP` are created eagerly when the root
container is initialized, while retaining the dependency, caching, and
shutdown behavior of dishka's `Scope.APP`. Both synchronous and asynchronous
containers support explicit initialization and initialization through their
context managers.

The implementation is designed to keep the integration with dishka minimally
intrusive. ashka-lifecycle extends the public provider and container construction APIs,
while leaving dishka's scope and factory implementations unchanged. The
`AshkaScope.BOOTSTRAP` value is only an ashka-side marker; the provider maps it
to dishka's native `Scope.APP` instead of introducing a new dishka scope.

ashka-lifecycle maintains its own registry of Bootstrap provider sources and the
corresponding dependency keys for each container. When a container is entered,
ashka-lifecycle looks up the registered keys and eagerly resolves them using the existing
container API. Synchronous containers resolve them one by one, while
asynchronous containers resolve them concurrently. This keeps the changes
localized to the public extension points and leaves dishka's existing scope,
caching, shutdown, and factory behavior in control.

`ashka-lifecycle` can also be installed and used independently from `ashka` as
an escape hatch. In this mode, manually import `ashka_lifecycle` and manually call `ashka_lifecycle.activate_lifecycle()` before
importing `dishka` to ensure that its patches are applied.

See more details and about how to use:

[English](https://github.com/handsome-Druid/ashka/blob/master/docs/en/features/bootstrap-lifecycle.md)
[中文](https://github.com/handsome-Druid/ashka/blob/master/docs/zh/features/bootstrap-lifecycle.md)