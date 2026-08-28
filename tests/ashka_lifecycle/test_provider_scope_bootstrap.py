from collections.abc import Generator
from typing import Any, Literal

from ashka import AshkaScope
from dishka import AnyOf, Provider, Scope, make_async_container, make_container, provide
from pytest import mark

a = False
b = False
c = False
d = False


class P(Provider):
    scope = AshkaScope.BOOTSTRAP

    @provide(provides=AnyOf[Literal["a"], str])
    @staticmethod
    def a():
        global a
        a = True
        yield "a"
        a = False

    @provide
    @staticmethod
    def b() -> Generator[Literal["b"], Any, None]:
        global b
        b = True
        yield "b"
        b = False


class AP(Provider):
    @provide(provides=str)
    @staticmethod
    async def c():
        global c
        c = True
        yield "c"
        c = False

    @provide(scope=Scope.REQUEST)
    @staticmethod
    def d() -> Generator[Literal["d"], Any, None]:
        global d
        d = True  # pragma: nocover
        yield "d"  # pragma: nocover
        d = False  # pragma: nocover


def test_container():
    assert a == b == c == d == False
    container = make_container(P())
    with container:
        assert a == b == True
        assert c == d == False
    assert a == b == c == d == False


@mark.asyncio
async def test_async_container():
    assert a == b == c == d == False
    acontainer1 = make_async_container(AP(AshkaScope.BOOTSTRAP))
    acontainer2 = make_async_container(P(), AP(scope=AshkaScope.BOOTSTRAP))
    async with acontainer1:
        assert c == True
        assert a == b == d == False
    async with acontainer2:
        assert a == b == c == True
        assert d == False
