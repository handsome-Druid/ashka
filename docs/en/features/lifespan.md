# Lifespan

After installing `ashka[lifecycle]`, use the framework-independent `lifespan`
provided by ashka to manage application container initialization and shutdown.
It provides synchronous and asynchronous versions and can be used with any
framework that supports binding a lifespan. Frameworks that do not support
lifespan binding can bind the corresponding `__enter__` and `__exit__`, or
`__aenter__` and `__aexit__`, operations to their startup and shutdown hooks.

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