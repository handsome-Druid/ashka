# Lifespan

安装 `ashka[lifecycle]` 后，可以使用 ashka 提供的、与具体框架无关的
`lifespan` 管理应用容器的初始化和关闭。它提供同步和异步版本，可以用于任何
支持绑定 lifespan 的框架。如果框架不支持绑定 lifespan，也可以将对应的
`__enter__` 和 `__exit__`，或 `__aenter__` 和 `__aexit__` 操作分别绑定到
启动和关闭挂钩。

如果需要自定义 lifespan，请将完整实现复制到自己的代码中修改，不要从本仓库
引入后尝试 patch。

在 FastAPI 中，可以直接绑定异步版本：

```python
from ashka import async_lifespan

app = FastAPI(lifespan=async_lifespan)
...
setup_dishka(container, app)
```