# Bootstrap 生命周期

此功能需要安装 `ashka[lifecycle]` extra。

`ashka` 为 dishka 容器增加了应用启动阶段。使用 `AshkaScope.BOOTSTRAP`
注册的依赖具有 dishka `Scope.APP` 的生命周期，但会在根容器初始化时
被主动解析。

在 dishka 的 scope 层级中，`Scope.RUNTIME` 是 `Scope.APP` 的外层，
`Scope.APP` 位于它的内层。因此 `Scope.APP` factory 可以依赖 `Scope.RUNTIME` factory，
但反向依赖不允许。`AshkaScope.BOOTSTRAP` 不是 dishka
新增的 scope，而是 ashka 的主动解析标记；ashka 会将它转换为 `Scope.APP`，
所以 bootstrap factory 遵循 APP scope 的依赖、缓存和关闭行为。

## 注册 Bootstrap 依赖

将 `AshkaScope.BOOTSTRAP` 传给 `ashka.provide`：

```python
from collections.abc import Iterator

from ashka import AshkaScope, make_container, provide
from dishka import Provider


class Database:
    def connect(self) -> None: ...

    def close(self) -> None: ...


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    def database(self) -> Iterator[Database]:
        database = Database()
        database.connect()
        yield database
        database.close()


container = make_container(ApplicationProvider())
```

dishka 创建 provide factory 时，必须通过返回类型或 `provides` 参数确定
factory 提供的依赖类型。因此，即使 bootstrap factory 只执行初始化操作、没有
有意义的返回值，也必须显式标注 `-> None`：

```python
class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    async def initialize(self) -> None: ...
```

如果 factory 提供的是其他类型，也可以使用 `provides` 参数显式指定类型。

### Bootstrap 依赖键冲突

ashka-lifecycle 修补后的 `make_container()` 和 `make_async_container()`
创建容器时，会检查每个 BOOTSTRAP factory 的 component 和提供的类型。这是
ashka-lifecycle 的行为，不是原版 dishka 工厂的行为。如果两个 factory 的
component 和类型相同，创建容器会抛出 `ValueError`。

必须进行此检查，因为 `init()` 会使用 component 和类型通过 `get()` 解析每个
bootstrap 依赖。两个 factory 使用相同的依赖键会使被解析的 factory 不明确。为了
确保每个 BOOTSTRAP factory 都能成功初始化，ashka-lifecycle 不允许这种重复。

避免冲突最简单的方法是使用不同的 component、返回 `Literal` 或 `NewType`，或者
使用 `provides` 重新指定不同的提供类型：

```python
from typing import Literal, NewType


class FirstProvider(Provider):
    component = "first"

    @provide(scope=AshkaScope.BOOTSTRAP)
    def resource(self) -> None: ...


class SecondProvider(Provider):
    component = "second"

    @provide(scope=AshkaScope.BOOTSTRAP)
    def resource(self) -> None: ...


class TypedProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    def literal_resource(self) -> Literal["resource"]: ...

    @provide(
        scope=AshkaScope.BOOTSTRAP,
        provides=NewType("ResourceName", str),
    )
    def named_resource(self): ...
```

不要把原生 dishka `Provider` 的 `scope` 属性直接设置为
`AshkaScope.BOOTSTRAP`。不允许这种用法，目前也没有支持该用法的计划。

`make_container()` 创建容器时只会登记 bootstrap 依赖，不会执行 ashka 的
生命周期 `container.init()`，也不会解析这些依赖。用户必须显式调用
`container.init()`，或者显式进入容器上下文，才能初始化数据库。初始化后的数据库
会在该容器的 APP 生命周期内保持缓存。

## 显式初始化

不使用容器上下文管理器时，必须显式调用 `init()`：

```python
container.init()
...
container.close()
```

如果测试需要持续创建多个 container，并且希望在关闭后清理 ashka 对 container
的引用，可以从 `ashka.entities.bootstrap.bootstrap_keys_by_container` 取出字典，
然后删除对应的键：

```python
from ashka.entities.bootstrap import bootstrap_keys_by_container

bootstrap_keys_by_container.pop(container, None)
```

异步版本使用 `make_async_container`，并等待两个生命周期操作：

```python
from collections.abc import AsyncIterator

from ashka import AshkaScope, make_async_container, provide
from dishka import Provider


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    async def database(self) -> AsyncIterator[Database]:
        database = Database()
        database.connect()
        yield database
        database.close()


container = make_async_container(ApplicationProvider())

await container.init()
...
await container.close()
```

## 初始化顺序

同步容器按照注册顺序依次初始化 bootstrap 依赖。每个依赖完成初始化后，才会开始
初始化下一个依赖。

异步容器通过 `asyncio.gather` 并发初始化 bootstrap 依赖，因此初始化顺序不是
顺序执行，也不应依赖该顺序。bootstrap 资源之间的依赖应通过 provider 参数表达，
而不是依赖注册顺序。

## 初始化失败

如果 `init()` 失败，同步容器和异步容器都不会自动清理已初始化的资源，也不会
自动关闭。初始化失败后的资源清理和容器关闭由调用方负责。

## 使用上下文管理器初始化

进入根容器的上下文时也会初始化 bootstrap 依赖。退出上下文会关闭容器，并释放
基于生成器管理的资源：

```python
with make_container(ApplicationProvider()) as container:
    ...
```

异步应用：

```python
async with make_async_container(ApplicationProvider()) as container:
    ...
```

## Bootstrap 与普通 Scope

初始化期间只会主动解析使用 `AshkaScope.BOOTSTRAP` 注册的 factory。直接使用
`Scope.APP` 或 `Scope.RUNTIME` 注册的 factory 都不会自动触发。换句话说，
`Scope.APP` 和 `Scope.RUNTIME` 只表示普通 factory 的 scope。使用
`AshkaScope.BOOTSTRAP` 注册时，ashka 会将该 factory 转换为 `Scope.APP`，
并在初始化时主动解析：

```python
from dishka import Scope


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    def database(self) -> Database:
        return Database()

    @provide(scope=Scope.APP)
    def cache(self) -> Cache:
        return Cache()

    @provide(scope=Scope.RUNTIME)
    def metrics(self) -> Metrics:
        return Metrics()
```

上例中的 `cache` 和 `metrics` 对应的 factory 都不会因为执行 `container.init()` 而创建，
只有首次调用 `container.get(Cache)` 或 `container.get(Metrics)` 时才会创建。只有将 factory
使用 `AshkaScope.BOOTSTRAP` 注册，所提供的依赖才会在 `container.init()` 或进入根容器时
自动触发；该 factory 实际使用 `Scope.APP` 生命周期，并在 APP 缓存中保持。

## 容器兼容性

导入 `ashka` 会全局修补 dishka 的 `Container`、`AsyncContainer`、
`make_container` 和 `make_async_container`。应先导入 `ashka`，再导入或保存
这些 dishka API 的引用。先导入 dishka 会产生警告，因为此前保存的引用可能绕过
ashka 的行为。

这些 monkey patch 保持了与上游 dishka 一致的接口路径，可以降低迁移时的认知负担。
它们用于兼容旧项目：只需优先导入 `ashka`，旧项目就不必立即修改原有的 dishka
导入。这是一种迁移辅助机制，不是稳定的长期用法；有空时应逐步将接口从 dishka
手动切换到 ashka，而不是长期依赖 monkey patch。

`ContainerType` 和 `AsyncContainerType` 用于向静态类型检查器描述 ashka 增加的
方法。工厂返回的是经过修补的 dishka 容器实例，而不是这些门面类的实例，因此
不要使用 `isinstance(container, ContainerType)` 或
`isinstance(container, AsyncContainerType)` 进行运行时判断。

Bootstrap source 以及每个容器对应的 bootstrap key 存储在进程级注册表中。
容器关闭沿用 dishka 的 `close()` 行为并清除容器缓存，因此应用可以创建多个
根容器，但必须关闭每个不再使用的容器。

容器必须通过 ashka 修补后的 `make_container` 或 `make_async_container` 工厂
创建，才能完成 bootstrap 注册。通过未修补的 dishka 工厂创建的容器仍可附加到
集成，但不会获得 ashka 的 bootstrap 依赖注册。

重复或并发调用 `init()` 时不会进行协调。初始化取消和部分失败也不会自动回滚。
应用必须串行执行初始化，每个容器只调用一次，并在关闭容器前清理所有已部分初始化
的资源。

## FastAPI Lifespan

FastAPI 的 lifespan 适合绑定容器的启动和关闭：

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from ashka import make_async_container
from ashka.integrations.fastapi import get_container, setup_dishka
from dishka import Provider
from fastapi import FastAPI


container = make_async_container(ApplicationProvider())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app_container = get_container(app)
    await app_container.init()
    yield
    await app_container.close()


app = FastAPI(lifespan=lifespan)
setup_dishka(container, app)
```