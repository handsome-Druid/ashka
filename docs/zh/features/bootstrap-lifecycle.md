# Bootstrap 生命周期

`ashka` 为 dishka 容器增加了应用启动阶段。使用 `AshkaScope.BOOTSTRAP`
注册的依赖具有 dishka `Scope.APP` 的生命周期，但会在根容器初始化时
被主动解析。

## 注册 Bootstrap 依赖

将 `AshkaScope.BOOTSTRAP` 传给 `ashka.provide`：

```python
from collections.abc import Iterator

from ashka import AshkaScope, make_container, provide
from dishka import Provider


class Database:
    def connect(self) -> None:
        ...

    def close(self) -> None:
        ...


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    def database(self) -> Iterator[Database]:
        database = Database()
        database.connect()
        yield database
        database.close()


container = make_container(ApplicationProvider())
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

## Runtime 依赖

初始化期间只会解析使用 `AshkaScope.BOOTSTRAP` 声明的 provider。普通的
`Scope.RUNTIME` provider 仍采用惰性创建，只会在首次请求时创建：

```python
from dishka import Scope


class ApplicationProvider(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    def database(self) -> Database:
        return Database()

    @provide(scope=Scope.RUNTIME)
    def metrics(self) -> Metrics:
        return Metrics()
```

执行 `container.init()` 后，`Database` 已存在于 app 缓存中，而 `Metrics`
仍会等到第一次调用 `container.get(Metrics)` 时才创建。

## 容器兼容性

导入 `ashka` 会全局修补 dishka 的 `Container`、`AsyncContainer`、
`make_container` 和 `make_async_container`。应先导入 `ashka`，再导入或保存
这些 dishka API 的引用。先导入 dishka 会产生警告，因为此前保存的引用可能绕过
ashka 的行为。

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