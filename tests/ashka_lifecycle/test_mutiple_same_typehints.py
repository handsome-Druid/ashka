from collections.abc import Generator
from typing import Literal, NewType

from ashka_lifecycle import (
    AshkaScope,
    make_async_container,
    make_container,
    provide,  # pyright: ignore[reportUnknownVariableType]
)

from dishka import Provider
from pytest import fixture

result: set[str] = set()


class P1(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    @staticmethod
    def r1() -> Generator[None, None, None]: ...

    @provide(scope=AshkaScope.BOOTSTRAP)
    @staticmethod
    def r11() -> Generator[None, None, None]: ...


class P2(Provider):
    component = "P2"

    @provide(scope=AshkaScope.BOOTSTRAP)
    @staticmethod
    def r2() -> Generator[None, None, None]:
        result.add("r2")
        yield
        result.remove("r2")

    @provide(scope=AshkaScope.BOOTSTRAP, provides=NewType("r22", str))
    @staticmethod
    def r22():
        result.add("r22")
        yield
        result.remove("r22")


class P3(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP, provides=Literal["r3"])
    @staticmethod
    def r3() -> Generator[None, None, None]:
        result.add("r3")
        yield
        result.remove("r3")

    @provide(scope=AshkaScope.BOOTSTRAP)
    @staticmethod
    def r33() -> Generator[None, None, None]:
        result.add("r33")
        yield
        result.remove("r33")


@fixture
def p1():

    return P1()


@fixture
def p2():
    return P2()


@fixture
def p3():
    return P3()


def test_past_conflict_dependency_key(p1: P1):
    # with raises(ValueError):
    make_container(p1)
    # with raises(ValueError):
    make_async_container(p1)


def test_compatible_dependency_keys(p2: P2, p3: P3):
    container = make_container(p2, p3)
    container.init()
    assert all(r in result for r in ("r2", "r22", "r3", "r33"))
    container.close()
    assert not result
