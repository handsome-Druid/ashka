from importlib import import_module
from subprocess import run
from sys import executable
from types import SimpleNamespace

from ashka.integrations import __all__, get_container, setup_dishka

from aiogram import Router
from aiohttp.web_app import Application
from arq import Worker
from celery import Celery  # pyright: ignore[reportMissingTypeStubs]
from click import Command, Context
from dishka import AsyncContainer, Container, make_async_container, make_container
from fastapi import FastAPI
from flask import Flask
from litestar import Litestar
from pytest import fixture, raises
from sanic import Config, Sanic
from starlette.applications import Starlette
from taskiq import AsyncBroker, BrokerMessage
from telebot import TeleBot


@fixture
def sanic():
    class Sanic_(Sanic[Config, SimpleNamespace]): ...

    return Sanic_(__name__)


@fixture
def flask():
    class Flask_(Flask): ...

    return Flask_(__name__)


@fixture
def fastapi():
    class FastAPI_(FastAPI): ...

    return FastAPI_()


@fixture
def starlette():
    class Starlette_(Starlette): ...

    return Starlette_()


@fixture
def aiohttp():
    class Application_(Application): ...

    return Application_()


@fixture
def litestar():
    class Litestar_(Litestar): ...

    return Litestar_()


@fixture
def aiogram():
    class Router_(Router): ...

    return Router_()


@fixture
def celery():
    class Celery_(Celery): ...

    return Celery_()


@fixture
def taskiq():
    class Broker(AsyncBroker):
        async def kick(self, message: BrokerMessage): ...

        async def listen(self):
            yield b""  # pragma: no cover

    return Broker()


@fixture
def arq():
    class Worker_(Worker): ...

    async def task(ctx: dict[object, object]): ...

    return Worker_([task])


@fixture
def click():
    class Context_(Context): ...

    return Context_(Command(__name__))


@fixture
def telebot():
    class TeleBot_(TeleBot): ...

    return TeleBot_("1:test")


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


def test_starlette(async_container: AsyncContainer, starlette: Starlette):
    setup_dishka(async_container, starlette)
    assert get_container(starlette) is async_container


def test_aiohttp(async_container: AsyncContainer, aiohttp: Application):
    setup_dishka(async_container, aiohttp)
    assert get_container(aiohttp) is async_container


def test_litestar(async_container: AsyncContainer, litestar: Litestar):
    setup_dishka(async_container, litestar)
    assert get_container(litestar) is async_container


def test_aiogram(async_container: AsyncContainer, aiogram: Router):
    setup_dishka(async_container, aiogram)
    assert get_container(aiogram) is async_container


def test_celery(container: Container, celery: Celery):
    setup_dishka(container, celery)
    assert get_container(celery) is container


def test_taskiq(async_container: AsyncContainer, taskiq: AsyncBroker):
    setup_dishka(async_container, taskiq)
    assert get_container(taskiq) is async_container


def test_arq(async_container: AsyncContainer, arq: Worker):
    setup_dishka(async_container, arq)
    assert get_container(arq) is async_container


def test_click(container: Container, click: Context):
    setup_dishka(container, click)
    assert get_container(click) is container


def test_telebot(container: Container, telebot: TeleBot):
    setup_dishka(container, telebot)
    assert get_container(telebot) is container


def test_type_error(async_container: AsyncContainer, fake_app: object = object()):
    with raises(TypeError):
        setup_dishka(async_container, fake_app)

    with raises(TypeError):
        get_container(fake_app)

    code = """
from importlib import util

from dishka import make_container
from pytest import raises


def find_spec(name, *args, **kwargs):
    return None

util.find_spec = find_spec

from ashka.integrations import setup_dishka, get_container

with raises(TypeError):
    setup_dishka(make_container(), object())

with raises(TypeError):
    get_container(object())
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_all():
    all = list(__all__)
    all.remove("get_container")
    all.remove("setup_dishka")

    for module in all:
        assert "test_" + module in globals()
        import_module("tests.ashka.integrations.test_" + module)
