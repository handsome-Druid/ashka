from types import SimpleNamespace

from ashka.integrations import get_container, setup_dishka

from dishka import AsyncContainer, Container, make_async_container, make_container
from fastapi import FastAPI
from flask import Flask
from pytest import fixture, raises
from sanic import Config, Sanic


@fixture
def sanic():
    return Sanic(__name__)


@fixture
def flask():
    return Flask(__name__)


@fixture
def fastapi():
    return FastAPI()


@fixture
def async_container():
    return make_async_container()


@fixture
def container():
    return make_container()


def test_sanic(async_container: AsyncContainer, sanic: Sanic[Config, SimpleNamespace]):
    setup_dishka(async_container, sanic)
    assert get_container(sanic) is async_container


def test_flask(container: Container, flask: Flask):
    setup_dishka(container, flask)
    assert get_container(flask) is container


def test_fastapi(async_container: AsyncContainer, fastapi: FastAPI):
    setup_dishka(async_container, fastapi)
    assert get_container(fastapi) is async_container


def test_import_error(async_container: AsyncContainer, fake_app: object = object()):
    with raises(ImportError):
        setup_dishka(async_container, fake_app)

    with raises(ImportError):
        get_container(fake_app)
