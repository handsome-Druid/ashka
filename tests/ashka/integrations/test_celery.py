from subprocess import run
from sys import executable

from ashka.integrations.celery import get_container, setup_dishka

from celery import Celery  # pyright: ignore[reportMissingTypeStubs]
from dishka import Container, make_container
from pytest import fixture


@fixture
def app():
    return Celery(__name__)


@fixture
def container():
    return make_container()


def test_container(app: Celery, container: Container):
    setup_dishka(container, app)
    assert app.conf["dishka_container"] is container  # pyright: ignore[reportUnknownMemberType]
    assert get_container(app) is container


def test_no_celery():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "celery":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import celery

assert not hasattr(celery, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
