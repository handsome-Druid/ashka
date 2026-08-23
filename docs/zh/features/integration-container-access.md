# 获取集成容器

每个 `ashka.integrations` 模块都在 `setup_dishka` 之外提供统一的
`get_container` 函数。应用的生命周期代码可以通过它获取此前附加到框架对象上的
同一个容器。

## 基本模式

从对应框架的集成模块导入这两个函数：

```python
from ashka import make_async_container
from ashka.integrations.fastapi import get_container, setup_dishka
from fastapi import FastAPI


app = FastAPI()
container = make_async_container(ApplicationProvider())

setup_dishka(container, app)

assert get_container(app) is container
```

`get_container` 返回传给 `setup_dishka` 的同一个容器，不会创建第二个容器。
传给 `setup_dishka` 的框架对象也必须传给 `get_container`。

## FastAPI 生产生命周期

可以在 FastAPI lifespan 中获取容器，无需再保留第二个应用级全局引用：

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from ashka import make_async_container
from ashka.integrations.fastapi import get_container, setup_dishka
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    container = get_container(app)
    await container.init()
    try:
        yield
    finally:
        await container.close()


app = FastAPI(lifespan=lifespan)
setup_dishka(make_async_container(ApplicationProvider()), app)
```

应用钩子、扩展和基础设施代码只要已经持有框架对象，就可以调用
`get_container(app)`。

## Celery 生产配置

同步集成使用相同的配置和获取模式：

```python
from ashka import make_container
from ashka.integrations.celery import get_container, setup_dishka
from celery import Celery


app = Celery("worker")
container = make_container(ApplicationProvider())

setup_dishka(container, app)
get_container(app).init()
```

Worker 关闭代码可以获取并关闭同一个容器：

```python
get_container(app).close()
```

## 框架特定的配置参数

集成模块保留对应 dishka 集成提供的配置签名和行为。框架需要时，可以向
`setup_dishka` 传入额外的位置参数和关键字参数：

```python
setup_dishka(container, app, auto_inject=True)
```

具体可选参数由所选 dishka 集成定义。

## 生命周期与配置要求

必须先成功调用 `setup_dishka`，才能调用 `get_container`。每个集成将容器存储在
框架特定的位置，因此在配置前调用 `get_container`，可能抛出该框架原生的
`AttributeError` 或 `KeyError`，而不是统一的 ashka 异常。

`get_container` 只获取已存储的引用，不会初始化或关闭容器，也不取得容器的
生命周期所有权。应用仍负责将 `init()` 与 `close()` 配对，或使用容器上下文
管理器。

多次调用配置可能替换已存储的容器引用，但不会关闭此前附加的容器。替换容器前，
应先关闭旧容器。

## 集成限制

FastAPI、Celery、Litestar 等框架包属于可选开发依赖，不会随 ashka 一起安装。
应用必须显式安装所需框架和 dishka
集成。

大多数可选框架依赖没有版本上限。部署前应一起验证所选框架和 dishka 版本。

导入期间会通过检查框架包是否可用来启用可选集成。加载已安装集成时发生的
`ImportError` 也可能导致该集成不可用，因此应在应用启动时验证中央配置入口。