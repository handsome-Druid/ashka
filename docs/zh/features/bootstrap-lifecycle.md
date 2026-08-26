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

from ashka import AshkaScope, provide
from dishka import Provider, make_container


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

不要把原生 dishka `Provider` 的 `scope` 属性直接设置为
`AshkaScope.BOOTSTRAP`。不允许这种用法，目前也没有支持该用法的计划。

`make_container()` 只负责创建容器，不会执行 ashka 的生命周期
`container.init()`，也不会解析 bootstrap 依赖。用户调用 `container.init()` 或
进入容器上下文时，ashka 会扫描容器的 registry，并解析其中的 bootstrap 依赖。
初始化后的数据库会在该容器的 APP 生命周期内保持缓存。

## 显式初始化

不使用容器上下文管理器时，必须显式调用 `init()`：

```python
container.init()
...
container.close()
```

异步版本使用 `make_async_container`，并等待两个生命周期操作：

```python
from collections.abc import AsyncIterator

from ashka import AshkaScope, provide
from dishka import Provider, make_async_container


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

安装 lifecycle extra 后，导入 `ashka` 会全局修补 dishka 的 `Container` 和
`AsyncContainer`。这些 patch 会添加 `init()`，并在进入容器上下文时初始化
bootstrap 依赖。`make_container` 和 `make_async_container` 仍是 dishka 的原生
工厂，可以直接从 `dishka` 导入。

使用生命周期方法前应先导入 `ashka`，确保容器 patch 已生效。

`ContainerType` 和 `AsyncContainerType` 用于向静态类型检查器描述新增的
`init()` 方法。dishka 原生工厂返回的是经过修补的 dishka 容器实例，而不是这些
门面类的实例，因此不要使用 `isinstance(container, ContainerType)` 或
`isinstance(container, AsyncContainerType)` 进行运行时判断。

初始化时，ashka 会遍历容器的 registry 链，并解析每个 registry 中的 bootstrap
dependency key。容器关闭沿用 dishka 的 `close()` 行为并清除容器缓存，因此应用
可以创建多个根容器，但必须关闭每个不再使用的容器。

重复或并发调用 `init()` 时不会进行协调。初始化取消和部分失败也不会自动回滚。
应用必须串行执行初始化，每个容器只调用一次，并在关闭容器前清理所有已部分初始化
的资源。

## FastAPI Lifespan

FastAPI 的 lifespan 适合绑定容器的启动和关闭：

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from ashka.integrations.fastapi import get_container, setup_dishka
from dishka import Provider, make_async_container
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