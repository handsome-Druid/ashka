from subprocess import run
from sys import executable

from ashka.integrations.litestar import get_container,setup_dishka

from dishka import AsyncContainer, make_async_container
from litestar import Litestar
from pytest import fixture


@fixture
def app():
    return Litestar()


@fixture
def async_container():
    return make_async_container()


def test_async_container(app: Litestar, async_container: AsyncContainer):
    setup_dishka(async_container, app)
    assert app.state.dishka_container is async_container
    assert get_container(app) is async_container


def test_no_litestar():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "litestar":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import litestar

assert not hasattr(litestar, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
