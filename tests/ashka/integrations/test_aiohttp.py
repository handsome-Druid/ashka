from subprocess import run
from sys import executable

from ashka.integrations.aiohttp import get_container

from aiohttp.web_app import Application
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiohttp import DISHKA_CONTAINER_KEY, setup_dishka
from pytest import fixture


@fixture
def app():
    return Application()


@fixture
def async_container():
    return make_async_container()


def test_async_container(app: Application, async_container: AsyncContainer):
    setup_dishka(async_container, app)
    assert app[DISHKA_CONTAINER_KEY] is async_container
    assert get_container(app) is async_container


def test_no_aiohttp():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "aiohttp":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import aiohttp

assert not hasattr(aiohttp, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
