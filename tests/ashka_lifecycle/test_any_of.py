from collections.abc import Generator

from ashka import AshkaScope
from dishka import AnyOf, Provider, make_async_container, make_container, provide
from pytest import mark

a = 0
b = 0
c = 0


class P(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP, provides=AnyOf[float, AnyOf[int, None]])
    @staticmethod
    def a():
        global a
        a += 1
        yield
        a -= 1

    @provide(scope=AshkaScope.BOOTSTRAP)
    @staticmethod
    def b() -> Generator[None, None, AnyOf[float, None]]:
        global b
        b += 1
        yield
        b -= 1

    @provide(scope=AshkaScope.BOOTSTRAP, provides=AnyOf[AnyOf[None, int], float])
    @staticmethod
    def c():
        global c
        c += 1
        yield
        c -= 1


def test_container():
    container = make_container(P())
    assert a == b == c == 0
    with container:
        assert a == b == c == 1
    assert a == b == c == 0


@mark.asyncio
async def test_async_container():
    container = make_async_container(P())
    assert a == b == c == 0
    async with container:
        assert a == b == c == 1
    assert a == b == c == 0
