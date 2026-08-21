from subprocess import run
from sys import executable

from ashka.integrations.fastapi import get_container, setup_dishka

from dishka import AsyncContainer, Container, make_async_container, make_container
from fastapi import FastAPI
from pytest import fixture


@fixture
def app():
    return FastAPI()


@fixture
def container():
    return make_container()


@fixture
def async_container():
    return make_async_container()


def test_container(app: FastAPI, container: Container):
    setup_dishka(container, app)
    assert app.state.dishka_container is container
    assert get_container(app) is container


def test_async_container(app: FastAPI, async_container: AsyncContainer):
    setup_dishka(async_container, app)
    assert app.state.dishka_container is async_container
    assert get_container(app) is async_container


def test_no_fastapi():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "fastapi":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import fastapi

assert not hasattr(fastapi, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
