from collections.abc import Generator

from ashka import (
    AshkaScope,
    lifespan,
    provide,  # pyright: ignore[reportUnknownVariableType]
)
from ashka.integrations import setup_dishka

from dishka import (
    AsyncContainer,
    Container,
    Provider,
    make_async_container,
    make_container,
)
from pytest import fixture, raises

result = 0


class P(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP)
    @staticmethod
    def _() -> Generator[None, None, None]:
        global result
        result = 1
        yield
        result = 0


@fixture
def container():
    return make_container(P())


@fixture
def async_container():
    return make_async_container(P())


def test_lifespan(container: Container):
    arq: dict[str, object] = {}
    setup_dishka(container, arq)
    assert result == 0
    lifespan_ = lifespan(arq)
    lifespan_.__enter__()
    assert result == 1
    lifespan_.__exit__(None, None, None)
    assert result == 0


def test_lifespan_with_async_container(async_container: AsyncContainer):
    arq: dict[str, object] = {}
    setup_dishka(async_container, arq)
    with raises(TypeError):
        lifespan(arq).__enter__()
