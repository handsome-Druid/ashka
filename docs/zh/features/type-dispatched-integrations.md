# 按类型分派集成

`ashka.integrations` 的中央入口根据框架对象的运行时类型选择集成，为所有受支持
框架提供统一的配置和容器访问导入路径。

## 中央入口

导入 `ashka` 后，通过 `ashka.integrations` 使用 `setup_dishka` 和 `get_container`：

```python
import ashka
```

两个函数都接受集成使用的框架对象。配置统一采用容器在前的调用形式：

```python
ashka.integrations.setup_dishka(container, app)
container = ashka.integrations.get_container(app)
```

框架对象的运行时类型决定调用哪个已注册集成。

## 与框架无关的配置

基础设施代码无需导入框架特定的 ashka 模块，即可获取容器并管理其生命周期：

```python
import ashka
from dishka import AsyncContainer, Container


container = ashka.integrations.get_container(app)

if isinstance(container, AsyncContainer):
    await container.init()
    ...
    await container.close()
elif isinstance(container, Container):
    container.init()
    ...
    container.close()
```

这里判断的是实际的 dishka 容器类型。`isinstance` 的第二个参数必须使用
`dishka.Container` 或 `dishka.AsyncContainer`，不可使用 ashka 中仅供类型标注的
`ashka.container.ContainerType` 或 `ashka.async_container.AsyncContainerType`；
对实际容器使用后两者一定返回 `False`。

同一组中央函数支持 Aiogram、Aiohttp、ARQ、Celery、Click、FastAPI、Flask、
Litestar、Sanic、Starlette、Taskiq 和 Telebot。

## 应用子类

分派遵循应用的类继承层次，因此框架子类会使用其框架基类的注册：

```python
import ashka
from fastapi import FastAPI


class Application(FastAPI):
    pass


app = Application()
container = ashka.make_async_container(ApplicationProvider())

ashka.integrations.setup_dishka(container, app)  # 相当于 ashka.integrations.fastapi.setup_dishka(container, app)
container = ashka.integrations.get_container(app)  # 相当于 ashka.integrations.fastapi.get_container(app)
```

项目可以使用自定义应用子类，无需增加第二个分派注册。

## 传递集成选项

额外参数会转发给所选集成：

```python
ashka.integrations.setup_dishka(container, app, auto_inject=True)
```

这样既能保留框架特定的配置选项，也能继续使用中央入口。

## 不支持的应用类型

如果对象类型没有对应的集成注册，中央函数会抛出 `TypeError` 并标识该类型：

```python
import ashka


class UnsupportedApplication:
    pass


ashka.integrations.get_container(UnsupportedApplication())
```

因此，缺少集成注册的问题会在应用配置阶段直接暴露。

## 分派限制

分派只使用框架对象的运行时类型。它不会验证传入的是同步还是异步容器、容器是否
由 ashka 创建，也不会验证容器是否与所选框架集成匹配。

导入 `ashka` 时会导入默认集成模块并安装注册。可用注册取决于已安装的可选依赖。

ARQ 的分派类型注册为 `dict`，因为 ARQ worker context 是字典。因此，传给中央
入口的任何字典都会被视为 ARQ context。

中央集成模块不会导入或注册 FastStream。选择使用 FastStream 支持的应用必须
显式导入 `ashka.integrations.faststream`，并遵循单独的 FastStream 支持说明。

对同一个应用对象再次调用配置，可能覆盖已存储的容器引用，但不会关闭旧容器。
应用必须显式管理容器替换和关闭。