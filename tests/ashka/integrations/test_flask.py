from subprocess import run
from sys import executable

from ashka.integrations.flask import get_container

from dishka import Container, make_container
from dishka.integrations.flask import setup_dishka
from flask import Flask
from pytest import fixture


@fixture
def app():
    return Flask(__name__)


@fixture
def container():
    return make_container()


def test_container(app: Flask, container: Container):
    setup_dishka(container, app)
    assert app.extensions["dishka_container"] is container
    assert get_container(app) is container


def test_no_flask():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "flask":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import flask

assert not hasattr(flask, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
