# Lifespan

The framework-independent `lifespan` provided by ashka enters and exits the
container context during application startup and shutdown. It provides
synchronous and asynchronous versions and can be used with any framework that
supports binding a lifespan. Frameworks that do not support lifespan binding
can bind the corresponding `__enter__` and `__exit__`, or `__aenter__` and
`__aexit__`, operations to their startup and shutdown hooks.

The lifespan helpers are available in the base `ashka` package. Install
`ashka[lifecycle]` when Bootstrap dependencies and the container `init()` API
are needed; entering a container then initializes its Bootstrap dependencies.

If you need a custom lifespan, copy the entire implementation into your code and
modify it there instead of importing it from this repository and trying to patch
it.

In FastAPI, bind the asynchronous version directly:

```python
from ashka import async_lifespan

app = FastAPI(lifespan=async_lifespan)
...
setup_dishka(container, app)
```