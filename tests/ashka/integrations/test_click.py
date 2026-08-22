from subprocess import run
from sys import executable

from ashka.integrations.click import get_container, setup_dishka

from click import Command, Context
from dishka import Container, make_container
from dishka.integrations.click import CONTAINER_NAME
from pytest import fixture


@fixture
def context():
    return Context(Command(__name__))


@fixture
def container():
    return make_container()


def test_container(context: Context, container: Container):
    setup_dishka(container, context)
    assert context.meta[CONTAINER_NAME] is container
    assert get_container(context) is container


def test_no_click():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "click":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import click

assert not hasattr(click, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
