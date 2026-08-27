# Lifespan

ashka 提供的、与具体框架无关的 `lifespan` 可以在应用启动和关闭时进入和退出
容器上下文。它提供同步和异步版本，可以用于任何支持绑定 lifespan 的框架。如果
框架不支持 lifespan 绑定，也可以将对应的 `__enter__` 和 `__exit__`，或
`__aenter__` 和 `__aexit__` 操作分别绑定到启动和关闭挂钩。

`lifespan` 辅助函数包含在基础包 `ashka` 中。只有在需要 Bootstrap 依赖和容器
`init()` API 时才需要安装 `ashka[lifecycle]`；安装后，进入容器时会初始化其中的
Bootstrap 依赖。

如果需要自定义 lifespan，请将完整实现复制到自己的代码中修改，不要从本仓库
引入后尝试 patch。

在 FastAPI 中，可以直接绑定异步版本：

```python
from ashka import async_lifespan

app = FastAPI(lifespan=async_lifespan)
...
setup_dishka(container, app)
```