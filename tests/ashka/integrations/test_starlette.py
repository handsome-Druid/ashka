from subprocess import run
from sys import executable

from ashka.integrations.starlette import get_container

from dishka import AsyncContainer, make_async_container
from dishka.integrations.starlette import setup_dishka
from pytest import fixture
from starlette.applications import Starlette


@fixture
def app():
    return Starlette()


@fixture
def async_container():
    return make_async_container()


def test_async_container(app: Starlette, async_container: AsyncContainer):
    setup_dishka(async_container, app)
    assert app.state.dishka_container is async_container
    assert get_container(app) is async_container


def test_no_starlette():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "starlette":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import starlette

assert not hasattr(starlette, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
